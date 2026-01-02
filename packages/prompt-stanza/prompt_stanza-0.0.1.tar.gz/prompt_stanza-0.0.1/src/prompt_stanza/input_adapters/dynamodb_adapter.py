"""DynamoDB adapter for loading prompts from AWS DynamoDB.

DynamoDB Table Schema:
----------------------
Table Name: prompt-stanzas (configurable)
Partition Key: identifier (String) - e.g., "code_review" or "engineering/code_review"
Sort Key: version (String) - e.g., "1.0.0"

Item Structure:
{
    "identifier": "code_review",           # Partition key
    "version": "1.0.0",                    # Sort key
    "name": "Code Review",                 # Prompt name
    "description": "Review code...",       # Optional description
    "template": {                          # Template (string or object)
        "system": "You are...",
        "task": "Review the following...",
        "output_format": "Provide...",     # Optional
        "use_sandwich_defense": false,     # Optional, default false
        "delimiting_strategy": "xml"       # Optional, default "none"
    },
    "schema": [                            # Optional validation schema
        {
            "name": "code",
            "type": "string",
            "description": "Code to review",
            "required": true
        }
    ],
    "defense_strategies": [                # Optional defense strategies
        "perplexity_check",
        "classify_intent"
    ],
    "created_at": "2025-01-15T10:30:00Z", # Timestamp (optional metadata)
    "updated_at": "2025-01-15T10:30:00Z", # Timestamp (optional metadata)
    "tags": ["engineering", "code"]        # Optional tags for filtering
}

GSI (Global Secondary Index) - Optional but recommended:
- Index Name: version-index
- Partition Key: identifier
- Sort Key: version
- Purpose: Efficient version queries and "latest" resolution

Creating the table (example using boto3):
```python
import boto3

dynamodb = boto3.client('dynamodb')

dynamodb.create_table(
    TableName='prompt-stanzas',
    KeySchema=[
        {'AttributeName': 'identifier', 'KeyType': 'HASH'},
        {'AttributeName': 'version', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'identifier', 'AttributeType': 'S'},
        {'AttributeName': 'version', 'AttributeType': 'S'}
    ],
    BillingMode='PAY_PER_REQUEST'
)
```
"""

from typing import Any

from ..exceptions import AdapterError, StanzaNotFoundError
from ..models import PromptConfig
from .base import BaseInputAdapter


class DynamoDBAdapter(BaseInputAdapter):
    """
    AWS DynamoDB adapter for loading prompts from DynamoDB tables.

    Features:
    - Load from DynamoDB with automatic version resolution
    - Query by identifier (partition key) and version (sort key)
    - "latest" version support using query + sort
    - Built-in caching with TTL support
    - Support for AWS credentials and custom endpoints

    Examples:
        adapter = DynamoDBAdapter(
            table_name="prompt-stanzas",
            region_name="us-east-1"
        )

        # Load latest version
        config = adapter.load("code_review")

        # Load specific version
        config = adapter.load("code_review", version="1.0.0")

        # Load from subdirectory-style identifier
        config = adapter.load("engineering/code_review", version="2.0.0")
    """

    def __init__(
        self,
        table_name: str = "prompt-stanzas",
        region_name: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        endpoint_url: str | None = None,
        cache_enabled: bool = True,
        cache_ttl: int | None = 3600,  # Default 1 hour
        max_cache_size: int | None = None,
        max_cache_memory_mb: float | None = None,
    ) -> None:
        """
        Initialize the DynamoDB adapter.

        Args:
            table_name: DynamoDB table name
            region_name: AWS region name (e.g., "us-east-1")
            aws_access_key_id: AWS access key ID (if not using default credentials)
            aws_secret_access_key: AWS secret access key
            endpoint_url: Custom DynamoDB endpoint URL (for local testing)
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
                "boto3 is required for DynamoDBAdapter. Install it with: pip install boto3"
            ) from e

        self.table_name = table_name

        # Initialize DynamoDB resource
        session_config = {}
        if region_name:
            session_config["region_name"] = region_name
        if aws_access_key_id:
            session_config["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            session_config["aws_secret_access_key"] = aws_secret_access_key

        dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url, **session_config)
        self.table = dynamodb.Table(table_name)

    def _query_latest_version(self, identifier: str) -> str | None:
        """
        Query DynamoDB to find the latest version for an identifier.

        Args:
            identifier: Prompt identifier

        Returns:
            Latest version string or None if not found
        """
        try:
            # Query all versions for this identifier
            response = self.table.query(
                KeyConditionExpression="identifier = :id",
                ExpressionAttributeValues={":id": identifier},
                ProjectionExpression="version",
            )

            items = response.get("Items", [])
            if not items:
                return None

            # Extract versions and sort
            versions = [item["version"] for item in items]
            versions.sort(key=self._parse_version)

            return versions[-1]  # Return highest version

        except Exception as e:
            raise AdapterError(
                f"Failed to query versions for '{identifier}' in DynamoDB: {e}"
            ) from e

    def _item_to_dict(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Convert DynamoDB item to prompt configuration dict.

        Args:
            item: DynamoDB item

        Returns:
            Dict suitable for PromptConfig
        """
        # Extract core fields
        config_dict = {
            "name": item["name"],
            "version": item["version"],
        }

        # Optional fields
        if "description" in item:
            config_dict["description"] = item["description"]

        if "template" in item:
            config_dict["template"] = item["template"]

        if "schema" in item:
            config_dict["schema"] = item["schema"]

        if "defense_strategies" in item:
            config_dict["defense_strategies"] = item["defense_strategies"]

        return config_dict

    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load a prompt configuration from DynamoDB.

        Args:
            identifier: Prompt identifier (partition key, e.g., "code_review")
            version: Version string (sort key, semver like "1.0.0" or "latest")

        Returns:
            Loaded and validated PromptConfig instance

        Raises:
            StanzaNotFoundError: If prompt cannot be found in DynamoDB
            AdapterError: If DynamoDB access or parsing fails
        """
        # Resolve "latest" version first
        resolved_version = version
        if version == "latest":
            resolved_version = self._query_latest_version(identifier)
            if not resolved_version:
                raise StanzaNotFoundError(
                    f"No versions found for prompt '{identifier}' in DynamoDB table "
                    f"'{self.table_name}'"
                )

        # Check cache with resolved version
        cached = self._load_from_cache(identifier, resolved_version)
        if cached is not None:
            return cached

        # Get item from DynamoDB
        try:
            response = self.table.get_item(
                Key={"identifier": identifier, "version": resolved_version}
            )

            if "Item" not in response:
                raise StanzaNotFoundError(
                    f"Prompt '{identifier}' version '{resolved_version}' not found in DynamoDB "
                    f"table '{self.table_name}'"
                )

            item = response["Item"]

            # Convert to config dict and compile
            config_dict = self._item_to_dict(item)
            config = self._compile_from_dict(config_dict)

            # Store in cache
            self._save_to_cache(identifier, resolved_version, config)

            return config

        except self.table.meta.client.exceptions.ResourceNotFoundException as err:
            raise AdapterError(f"DynamoDB table '{self.table_name}' does not exist") from err
        except ValueError as e:
            raise AdapterError(
                f"Invalid prompt configuration for '{identifier}' v{resolved_version}: {e}"
            ) from e
        except Exception as e:
            if "StanzaNotFoundError" in str(type(e).__name__):
                raise
            raise AdapterError(
                f"Failed to load '{identifier}' v{resolved_version} from DynamoDB: {e}"
            ) from e
