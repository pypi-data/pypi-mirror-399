"""Input adapters for loading prompt templates from various sources."""

from .base import BaseInputAdapter
from .dynamodb_adapter import DynamoDBAdapter
from .inline_adapter import InlineAdapter
from .local_file_adapter import LocalFileAdapter
from .mongodb_adapter import MongoDBAdapter
from .s3_file_adapter import S3FileAdapter
from .sql_adapter import SQLAdapter

__all__ = [
    "BaseInputAdapter",
    "DynamoDBAdapter",
    "InlineAdapter",
    "LocalFileAdapter",
    "MongoDBAdapter",
    "S3FileAdapter",
    "SQLAdapter",
]
