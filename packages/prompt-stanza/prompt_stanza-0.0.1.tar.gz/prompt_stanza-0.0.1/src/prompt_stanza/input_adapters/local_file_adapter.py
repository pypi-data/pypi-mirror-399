"""Local file system adapter supporting JSON and YAML formats."""

import json
from pathlib import Path

import yaml

from ..exceptions import AdapterError, StanzaNotFoundError
from ..models import PromptConfig
from .base import BaseInputAdapter


class LocalFileAdapter(BaseInputAdapter):
    """
    Local file system adapter for loading prompts from JSON or YAML files.

    Stores prompts as JSON/YAML files in the structure:
    {base_directory}/{subdirectory}/{identifier}/{version}.{json|yaml}
    or
    {base_directory}/{identifier}/{version}.{json|yaml}

    Features:
    - Load from local file system with subdirectory support
    - Automatic format detection (JSON or YAML)
    - Automatic version resolution ("latest" finds highest semver)
    - Built-in caching with TTL support
    - Lazy loading on first access

    Examples:
        adapter = LocalFileAdapter(base_directory="./prompts")

        # Load latest version (auto-detects JSON or YAML)
        config = adapter.load("code_review")

        # Load specific version
        config = adapter.load("code_review", version="1.0.0")

        # Load from subdirectory
        config = adapter.load("engineering/code_review", version="2.0.0")
    """

    def __init__(
        self,
        base_directory: str | Path = "./prompts",
        cache_enabled: bool = True,
        cache_ttl: int | None = None,
        max_cache_size: int | None = None,
        max_cache_memory_mb: float | None = None,
    ) -> None:
        """
        Initialize the local file system adapter.

        Args:
            base_directory: Base directory for storing files
            cache_enabled: Whether to cache loaded prompts in memory
            cache_ttl: Cache time-to-live in seconds. None means no expiration.
            max_cache_size: Maximum number of items in cache
            max_cache_memory_mb: Maximum cache memory in MB
        """
        super().__init__(
            cache_enabled=cache_enabled,
            cache_ttl=cache_ttl,
            max_cache_size=max_cache_size,
            max_cache_memory_mb=max_cache_memory_mb,
        )
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)

    def _get_identifier_path(self, identifier: str) -> Path:
        """
        Get the directory path for an identifier (handles subdirectories).

        Args:
            identifier: Prompt identifier (e.g., "code_review" or "engineering/code_review")

        Returns:
            Full path to the identifier directory
        """
        return self.base_directory / identifier

    def _list_versions(self, identifier: str) -> list[tuple[str, str]]:
        """
        List all available versions for an identifier.

        Args:
            identifier: Prompt identifier (can include subdirectories)

        Returns:
            Sorted list of (version, format) tuples where format is 'json' or 'yaml'
        """
        identifier_dir = self._get_identifier_path(identifier)

        if not identifier_dir.exists() or not identifier_dir.is_dir():
            return []

        # Find both JSON and YAML files
        version_files = list(identifier_dir.glob("*.yaml")) + list(identifier_dir.glob("*.json"))
        versions = [(f.stem, f.suffix[1:]) for f in version_files]

        # Sort by semantic version
        try:
            versions.sort(key=lambda x: self._parse_version(x[0]))
        except (ValueError, AttributeError):
            # Fallback to string sort if version parsing fails
            versions.sort(key=lambda x: x[0])

        return versions

    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load a prompt configuration from a JSON or YAML file.

        Args:
            identifier: Prompt identifier (can include subdirectories like
                "engineering/code_review")
            version: Version string (semver like "1.0.0" or "latest" for highest version)

        Returns:
            Loaded and validated PromptConfig instance

        Raises:
            StanzaNotFoundError: If prompt file cannot be found
            AdapterError: If file parsing or validation fails
        """
        # Resolve "latest" version first
        resolved_version = version
        file_format = None

        if version == "latest":
            versions = self._list_versions(identifier)
            if not versions:
                raise StanzaNotFoundError(
                    f"No versions found for prompt '{identifier}' in {self.base_directory}"
                )
            resolved_version, file_format = versions[-1]  # Highest semver

        # Check cache with resolved version
        cached = self._load_from_cache(identifier, resolved_version)
        if cached is not None:
            return cached

        # Construct file path
        identifier_dir = self._get_identifier_path(identifier)
        if not identifier_dir.exists():
            raise StanzaNotFoundError(f"Prompt '{identifier}' not found at {identifier_dir}")

        # Try to find the file (check both formats if not specified)
        if file_format:
            file_path = identifier_dir / f"{resolved_version}.{file_format}"
            if not file_path.exists():
                raise StanzaNotFoundError(
                    f"Prompt '{identifier}' version '{resolved_version}' not found at {file_path}"
                )
        else:
            # Try YAML first, then JSON
            yaml_path = identifier_dir / f"{resolved_version}.yaml"
            json_path = identifier_dir / f"{resolved_version}.json"

            if yaml_path.exists():
                file_path = yaml_path
                file_format = "yaml"
            elif json_path.exists():
                file_path = json_path
                file_format = "json"
            else:
                raise StanzaNotFoundError(
                    f"Prompt '{identifier}' version '{resolved_version}' not found "
                    "(tried .yaml and .json)"
                )

        # Load and parse file
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse based on format
            if file_format == "json":
                data = json.loads(content)
                config = self._compile_from_dict(data)
            else:  # yaml
                config = self._compile(content)

            # Store in cache
            self._save_to_cache(identifier, resolved_version, config)

            return config

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise AdapterError(
                f"Failed to parse {file_format.upper()} file at {file_path}: {e}"
            ) from e
        except ValueError as e:
            raise AdapterError(f"Invalid prompt configuration in {file_path}: {e}") from e
        except OSError as e:
            raise AdapterError(f"Failed to read file {file_path}: {e}") from e
