"""MongoDB adapter for loading prompts from MongoDB collections.

MongoDB Collection Schema:
--------------------------
Collection Name: prompt_stanzas (configurable)
Database Name: prompts (configurable)

Document Structure:
{
    "_id": ObjectId("..."),                # MongoDB auto-generated ID
    "identifier": "code_review",           # Prompt identifier (indexed)
    "version": "1.0.0",                    # Semantic version (indexed)
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
    "created_at": ISODate("2025-01-15T10:30:00Z"),  # Timestamp (optional)
    "updated_at": ISODate("2025-01-15T10:30:00Z"),  # Timestamp (optional)
    "tags": ["engineering", "code"],       # Optional tags
    "metadata": {                          # Optional additional metadata
        "author": "John Doe",
        "team": "Engineering"
    }
}

Indexes (recommended):
1. Compound unique index on (identifier, version) for fast lookups
2. Index on identifier for version queries
3. Optional: Index on tags for filtering

Creating indexes (example using pymongo):
```python
from pymongo import MongoClient, ASCENDING

client = MongoClient("mongodb://localhost:27017/")
db = client["prompts"]
collection = db["prompt_stanzas"]

# Unique compound index for identifier + version
collection.create_index(
    [("identifier", ASCENDING), ("version", ASCENDING)],
    unique=True,
    name="identifier_version_idx"
)

# Index for identifier queries
collection.create_index("identifier", name="identifier_idx")

# Optional: Index for tags
collection.create_index("tags", name="tags_idx")
```

JSON Schema Validation (optional but recommended):
```python
db.command({
    "collMod": "prompt_stanzas",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["identifier", "version", "name", "template"],
            "properties": {
                "identifier": {"bsonType": "string"},
                "version": {
                    "bsonType": "string",
                    "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
                },
                "name": {"bsonType": "string"},
                "description": {"bsonType": "string"},
                "template": {
                    "bsonType": ["string", "object"]
                },
                "schema": {"bsonType": "array"},
                "defense_strategies": {"bsonType": "array"}
            }
        }
    }
})
```
"""

from typing import Any

from ..exceptions import AdapterError, StanzaNotFoundError
from ..models import PromptConfig
from .base import BaseInputAdapter


class MongoDBAdapter(BaseInputAdapter):
    """
    MongoDB adapter for loading prompts from MongoDB collections.

    Features:
    - Load from MongoDB with automatic version resolution
    - Query by identifier and version (compound index)
    - "latest" version support using aggregation
    - Built-in caching with TTL support
    - Support for authentication and SSL/TLS

    Examples:
        adapter = MongoDBAdapter(
            connection_string="mongodb://localhost:27017/",
            database_name="prompts",
            collection_name="prompt_stanzas"
        )

        # Load latest version
        config = adapter.load("code_review")

        # Load specific version
        config = adapter.load("code_review", version="1.0.0")

        # Load with subdirectory-style identifier
        config = adapter.load("engineering/code_review", version="2.0.0")
    """

    def __init__(
        self,
        connection_string: str = "mongodb://localhost:27017/",
        database_name: str = "prompts",
        collection_name: str = "prompt_stanzas",
        cache_enabled: bool = True,
        cache_ttl: int | None = 3600,  # Default 1 hour
        max_cache_size: int | None = None,
        max_cache_memory_mb: float | None = None,
    ) -> None:
        """
        Initialize the MongoDB adapter.

        Args:
            connection_string: MongoDB connection string (e.g., "mongodb://localhost:27017/")
            database_name: Database name
            collection_name: Collection name for storing prompts
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
            from pymongo import MongoClient
        except ImportError as e:
            raise ImportError(
                "pymongo is required for MongoDBAdapter. Install it with: pip install pymongo"
            ) from e

        self.database_name = database_name
        self.collection_name = collection_name

        # Initialize MongoDB client
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def _query_latest_version(self, identifier: str) -> str | None:
        """
        Query MongoDB to find the latest version for an identifier.

        Args:
            identifier: Prompt identifier

        Returns:
            Latest version string or None if not found
        """
        try:
            # Find all versions for this identifier
            cursor = self.collection.find({"identifier": identifier}, {"version": 1, "_id": 0})

            versions = [doc["version"] for doc in cursor]
            if not versions:
                return None

            # Sort by semantic version
            versions.sort(key=self._parse_version)

            return versions[-1]  # Return highest version

        except Exception as e:
            raise AdapterError(
                f"Failed to query versions for '{identifier}' in MongoDB: {e}"
            ) from e

    def _document_to_dict(self, document: dict[str, Any]) -> dict[str, Any]:
        """
        Convert MongoDB document to prompt configuration dict.

        Args:
            document: MongoDB document

        Returns:
            Dict suitable for PromptConfig
        """
        # Extract core fields
        config_dict = {
            "name": document["name"],
            "version": document["version"],
        }

        # Optional fields
        if "description" in document:
            config_dict["description"] = document["description"]

        if "template" in document:
            config_dict["template"] = document["template"]

        if "schema" in document:
            config_dict["schema"] = document["schema"]

        if "defense_strategies" in document:
            config_dict["defense_strategies"] = document["defense_strategies"]

        return config_dict

    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load a prompt configuration from MongoDB.

        Args:
            identifier: Prompt identifier (e.g., "code_review")
            version: Version string (semver like "1.0.0" or "latest")

        Returns:
            Loaded and validated PromptConfig instance

        Raises:
            StanzaNotFoundError: If prompt cannot be found in MongoDB
            AdapterError: If MongoDB access or parsing fails
        """
        # Resolve "latest" version first
        resolved_version = version
        if version == "latest":
            resolved_version = self._query_latest_version(identifier)
            if not resolved_version:
                raise StanzaNotFoundError(
                    f"No versions found for prompt '{identifier}' in MongoDB collection "
                    f"'{self.database_name}.{self.collection_name}'"
                )

        # Check cache with resolved version
        cached = self._load_from_cache(identifier, resolved_version)
        if cached is not None:
            return cached

        # Query MongoDB for the document
        try:
            document = self.collection.find_one(
                {"identifier": identifier, "version": resolved_version}
            )

            if not document:
                raise StanzaNotFoundError(
                    f"Prompt '{identifier}' version '{resolved_version}' not found in MongoDB "
                    f"collection '{self.database_name}.{self.collection_name}'"
                )

            # Convert to config dict and compile
            config_dict = self._document_to_dict(document)
            config = self._compile_from_dict(config_dict)

            # Store in cache
            self._save_to_cache(identifier, resolved_version, config)

            return config

        except ValueError as e:
            raise AdapterError(
                f"Invalid prompt configuration for '{identifier}' v{resolved_version}: {e}"
            ) from e
        except Exception as e:
            if "StanzaNotFoundError" in str(type(e).__name__):
                raise
            raise AdapterError(
                f"Failed to load '{identifier}' v{resolved_version} from MongoDB: {e}"
            ) from e

    def close(self) -> None:
        """Close MongoDB connection."""
        if hasattr(self, "client"):
            self.client.close()

    def __del__(self):
        """Cleanup MongoDB connection on deletion."""
        self.close()
