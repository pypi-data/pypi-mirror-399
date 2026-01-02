"""Utility to create MongoDB collection with indexes for prompt stanzas."""


def setup_mongodb_collection(
    connection_string: str = "mongodb://localhost:27017/",
    database_name: str = "prompts",
    collection_name: str = "prompt_stanzas",
    create_indexes: bool = True,
    add_validation: bool = True,
) -> dict:
    """
    Create MongoDB collection with indexes and validation for prompt stanzas.

    Collection Schema:
    - Compound unique index on (identifier, version)
    - Index on identifier for queries
    - Optional JSON schema validation

    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database
        collection_name: Name of the collection
        create_indexes: Whether to create indexes
        add_validation: Whether to add JSON schema validation

    Returns:
        Dictionary with creation status

    Raises:
        ImportError: If pymongo is not installed
        Exception: If collection/index creation fails

    Example:
        >>> setup_mongodb_collection(
        ...     connection_string="mongodb://localhost:27017/",
        ...     database_name="prompts",
        ...     collection_name="prompt_stanzas"
        ... )
    """
    try:
        from pymongo import ASCENDING, MongoClient
    except ImportError as e:
        raise ImportError("pymongo is required. Install it with: pip install pymongo") from e

    # Initialize MongoDB client
    client = MongoClient(connection_string)
    db = client[database_name]

    # Create collection if it doesn't exist
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print(f"✓ MongoDB collection '{database_name}.{collection_name}' created")
    else:
        print(f"✓ MongoDB collection '{database_name}.{collection_name}' already exists")

    collection = db[collection_name]
    results = {"collection": "created"}

    # Create indexes
    if create_indexes:
        try:
            # Compound unique index on identifier + version
            collection.create_index(
                [("identifier", ASCENDING), ("version", ASCENDING)],
                unique=True,
                name="identifier_version_idx",
            )
            print("  ✓ Created unique index: identifier_version_idx")

            # Index on identifier for queries
            collection.create_index("identifier", name="identifier_idx")
            print("  ✓ Created index: identifier_idx")

            # Optional: Index on tags
            collection.create_index("tags", name="tags_idx")
            print("  ✓ Created index: tags_idx")

            results["indexes"] = "created"
        except Exception as e:
            print(f"  ⚠ Index creation warning: {e}")
            results["indexes"] = "exists"

    # Add JSON schema validation
    if add_validation:
        try:
            db.command(
                {
                    "collMod": collection_name,
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["identifier", "version", "name", "template"],
                            "properties": {
                                "identifier": {
                                    "bsonType": "string",
                                    "description": "Prompt identifier (required)",
                                },
                                "version": {
                                    "bsonType": "string",
                                    "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
                                    "description": "Semantic version (required)",
                                },
                                "name": {
                                    "bsonType": "string",
                                    "description": "Prompt name (required)",
                                },
                                "description": {
                                    "bsonType": "string",
                                    "description": "Prompt description (optional)",
                                },
                                "template": {
                                    "bsonType": ["string", "object"],
                                    "description": "Template string or object (required)",
                                },
                                "schema": {
                                    "bsonType": "array",
                                    "description": "Input validation schema (optional)",
                                },
                                "defense_strategies": {
                                    "bsonType": "array",
                                    "description": "Defense strategies list (optional)",
                                },
                                "tags": {
                                    "bsonType": "array",
                                    "description": "Tags for filtering (optional)",
                                },
                            },
                        }
                    },
                    "validationLevel": "moderate",  # Allow existing docs to violate
                    "validationAction": "warn",  # Warn on validation failure
                }
            )
            print("  ✓ JSON schema validation added")
            results["validation"] = "added"
        except Exception as e:
            print(f"  ⚠ Validation setup warning: {e}")
            results["validation"] = "failed"

    client.close()
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup MongoDB collection for prompt stanzas")
    parser.add_argument(
        "--connection-string",
        default="mongodb://localhost:27017/",
        help="MongoDB connection string (default: mongodb://localhost:27017/)",
    )
    parser.add_argument(
        "--database",
        default="prompts",
        help="Database name (default: prompts)",
    )
    parser.add_argument(
        "--collection",
        default="prompt_stanzas",
        help="Collection name (default: prompt_stanzas)",
    )
    parser.add_argument(
        "--no-indexes",
        action="store_true",
        help="Skip index creation",
    )
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip JSON schema validation",
    )

    args = parser.parse_args()

    setup_mongodb_collection(
        connection_string=args.connection_string,
        database_name=args.database,
        collection_name=args.collection,
        create_indexes=not args.no_indexes,
        add_validation=not args.no_validation,
    )
