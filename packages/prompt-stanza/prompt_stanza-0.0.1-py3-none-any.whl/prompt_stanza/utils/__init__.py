"""Utility scripts for creating and managing database tables/collections."""

from .create_dynamodb_table import create_dynamodb_table
from .create_mongodb_collection import setup_mongodb_collection

__all__ = [
    "create_dynamodb_table",
    "setup_mongodb_collection",
]
