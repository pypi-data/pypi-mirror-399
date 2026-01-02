"""S3 adapter for loading prompts from AWS S3."""

import json

import yaml

from ..exceptions import AdapterError, StanzaNotFoundError
from ..models import PromptConfig
from .base import BaseInputAdapter


class S3FileAdapter(BaseInputAdapter):
    """
    AWS S3 adapter for loading prompts from S3 buckets.

    Stores prompts as JSON/YAML files in S3 with the structure:
    s3://{bucket_name}/{prefix}/{identifier}/{version}.{json|yaml}

    Features:
    - Load from S3 with automatic format detection (JSON or YAML)
    - Automatic version resolution ("latest" finds highest semver)
    - Built-in caching with TTL support
    - Support for AWS credentials and custom endpoints

    Examples:
        adapter = S3FileAdapter(
            bucket_name="my-prompts-bucket",
            prefix="prompts"
        )

        # Load latest version
        config = adapter.load("code_review")

        # Load specific version
        config = adapter.load("code_review", version="1.0.0")

        # Load from subdirectory
        config = adapter.load("engineering/code_review", version="2.0.0")
    """

    def __init__(
        self,
        bucket_name: str,
        prefix: str = "",
        region_name: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        endpoint_url: str | None = None,
        cache_enabled: bool = True,
        cache_ttl: int | None = 3600,  # Default 1 hour for S3
        max_cache_size: int | None = None,
        max_cache_memory_mb: float | None = None,
    ) -> None:
        """
        Initialize the S3 adapter.

        Args:
            bucket_name: S3 bucket name
            prefix: Prefix/path within the bucket (e.g., "prompts" or "prod/prompts")
            region_name: AWS region name (e.g., "us-east-1")
            aws_access_key_id: AWS access key ID (if not using default credentials)
            aws_secret_access_key: AWS secret access key
            endpoint_url: Custom S3 endpoint URL (for S3-compatible services)
            cache_enabled: Whether to cache loaded prompts in memory
            cache_ttl: Cache time-to-live in seconds
            max_cache_size: Maximum number of items in cache
            max_cache_memory_mb: Maximum cache memory in MB
        """
        super().__init__(
            cache_enabled=cache_enabled,
            cache_ttl=cache_ttl,
            max_cache_size=max_cache_size,
            max_cache_memory_mb=max_cache_memory_mb,
        )

        try:
            import boto3
        except ImportError as e:
            raise ImportError(
                "boto3 is required for S3FileAdapter. Install it with: pip install boto3"
            ) from e

        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/")

        # Initialize S3 client
        session_config = {}
        if region_name:
            session_config["region_name"] = region_name
        if aws_access_key_id:
            session_config["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            session_config["aws_secret_access_key"] = aws_secret_access_key

        self.s3_client = boto3.client("s3", endpoint_url=endpoint_url, **session_config)

    def _get_s3_prefix(self, identifier: str) -> str:
        """
        Get the S3 prefix for an identifier.

        Args:
            identifier: Prompt identifier (e.g., "code_review" or "engineering/code_review")

        Returns:
            Full S3 prefix
        """
        if self.prefix:
            return f"{self.prefix}/{identifier}/"
        return f"{identifier}/"

    def _list_versions(self, identifier: str) -> list[tuple[str, str]]:
        """
        List all available versions for an identifier in S3.

        Args:
            identifier: Prompt identifier (can include subdirectories)

        Returns:
            Sorted list of (version, format) tuples where format is 'json' or 'yaml'
        """
        prefix = self._get_s3_prefix(identifier)

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix, Delimiter="/"
            )

            if "Contents" not in response:
                return []

            versions = []
            for obj in response["Contents"]:
                key = obj["Key"]
                # Extract filename from key
                filename = key.split("/")[-1]

                # Check if it's a version file (ends with .json or .yaml)
                if filename.endswith(".json"):
                    version = filename[:-5]  # Remove .json
                    versions.append((version, "json"))
                elif filename.endswith(".yaml"):
                    version = filename[:-5]  # Remove .yaml
                    versions.append((version, "yaml"))

            # Sort by semantic version
            try:
                versions.sort(key=lambda x: self._parse_version(x[0]))
            except (ValueError, AttributeError):
                # Fallback to string sort if version parsing fails
                versions.sort(key=lambda x: x[0])

            return versions

        except Exception as e:
            raise AdapterError(f"Failed to list versions for '{identifier}' in S3: {e}") from e

    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load a prompt configuration from S3.

        Args:
            identifier: Prompt identifier (can include subdirectories like
                "engineering/code_review")
            version: Version string (semver like "1.0.0" or "latest" for highest version)

        Returns:
            Loaded and validated PromptConfig instance

        Raises:
            StanzaNotFoundError: If prompt cannot be found in S3
            AdapterError: If S3 access or parsing fails
        """
        # Resolve "latest" version first
        resolved_version = version
        file_format = None

        if version == "latest":
            versions = self._list_versions(identifier)
            if not versions:
                raise StanzaNotFoundError(
                    f"No versions found for prompt '{identifier}' in s3://{self.bucket_name}/{self.prefix}"
                )
            resolved_version, file_format = versions[-1]  # Highest semver

        # Check cache with resolved version
        cached = self._load_from_cache(identifier, resolved_version)
        if cached is not None:
            return cached

        # Construct S3 key
        prefix = self._get_s3_prefix(identifier)

        # Try to find the file (check both formats if not specified)
        s3_key = None
        if file_format:
            s3_key = f"{prefix}{resolved_version}.{file_format}"
        else:
            from botocore.exceptions import ClientError

            # Try YAML first, then JSON
            yaml_key = f"{prefix}{resolved_version}.yaml"
            json_key = f"{prefix}{resolved_version}.json"

            # Check if YAML exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=yaml_key)
                s3_key = yaml_key
                file_format = "yaml"
            except ClientError as err:
                error_code = err.response.get("Error", {}).get("Code")
                if error_code not in {"404", "NoSuchKey", "NotFound"}:
                    raise AdapterError(f"Failed checking S3 key {yaml_key}: {error_code}") from err
                # Try JSON
                try:
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=json_key)
                    s3_key = json_key
                    file_format = "json"
                except ClientError as err2:
                    error_code = err2.response.get("Error", {}).get("Code")
                    if error_code not in {"404", "NoSuchKey", "NotFound"}:
                        raise AdapterError(
                            f"Failed checking S3 key {json_key}: {error_code}"
                        ) from err2
                    raise StanzaNotFoundError(
                        f"Prompt '{identifier}' version '{resolved_version}' not found in S3 "
                        "(tried .yaml and .json)"
                    ) from None

        # Load and parse file from S3
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response["Body"].read().decode("utf-8")

            # Parse based on format
            if file_format == "json":
                data = json.loads(content)
                config = self._compile_from_dict(data)
            else:  # yaml
                config = self._compile(content)

            # Store in cache
            self._save_to_cache(identifier, resolved_version, config)

            return config

        except self.s3_client.exceptions.NoSuchKey as err:
            raise StanzaNotFoundError(
                f"Prompt '{identifier}' version '{resolved_version}' not found at s3://{self.bucket_name}/{s3_key}"
            ) from err
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise AdapterError(
                f"Failed to parse {file_format.upper()} from S3 key {s3_key}: {e}"
            ) from e
        except ValueError as e:
            raise AdapterError(f"Invalid prompt configuration from S3 key {s3_key}: {e}") from e
        except Exception as e:
            raise AdapterError(f"Failed to load from S3 key {s3_key}: {e}") from e
