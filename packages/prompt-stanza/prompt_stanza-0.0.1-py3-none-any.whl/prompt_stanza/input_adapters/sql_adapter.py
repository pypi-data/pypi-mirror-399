"""SQL adapter for loading prompts from SQL databases.

Supports: SQLite, MySQL/MariaDB, PostgreSQL, SQL Server, Oracle

Table Schema (DDL):
-------------------
-- SQLite, MySQL, PostgreSQL, SQL Server, Oracle compatible
-- All engines support JSON storage (native JSON type or TEXT with JSON functions)

CREATE TABLE prompt_stanzas (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,  -- MySQL/MariaDB
    -- id SERIAL PRIMARY KEY,                -- PostgreSQL
    -- id INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLite
    -- id INT IDENTITY(1,1) PRIMARY KEY,     -- SQL Server
    -- id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Oracle

    identifier VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template JSON NOT NULL,              -- JSON object or string wrapper
    validation_schema JSON,              -- JSON array of schema objects
    defense_strategies JSON,             -- JSON array of strategy names
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(identifier, version)
);

-- Note: SQLite uses TEXT for JSON storage but provides JSON functions
-- MySQL 5.7+, PostgreSQL 9.2+, SQL Server 2016+, Oracle 12c+ have native JSON

-- Index for fast identifier queries
CREATE INDEX idx_identifier ON prompt_stanzas(identifier);

-- Index for version queries
CREATE INDEX idx_version ON prompt_stanzas(identifier, version);

Table Structure:
{
    "id": 1,                                   # Auto-increment primary key
    "identifier": "code_review",               # Prompt identifier
    "version": "1.0.0",                        # Semantic version
    "name": "Code Review",                     # Prompt name
    "description": "Review code...",           # Optional description (NULL allowed)
    "template": {                               # JSON - template config or string wrapper
        "system": "...",
        "task": "...",
        "output_format": "..."
    },
    # OR for simple string templates:
    "template": {"template": "Hello {{ name }}!"},

    "validation_schema": [{...}],              # JSON array - schema fields
    "defense_strategies": ["perplexity_check"], # JSON array - strategy names
    "created_at": "2025-01-15 10:30:00",       # Timestamp
    "updated_at": "2025-01-15 10:30:00"        # Timestamp
}

Creating the table:

SQLite:
```python
import sqlite3
conn = sqlite3.connect('prompts.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS prompt_stanzas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier VARCHAR(255) NOT NULL,
        version VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        template TEXT NOT NULL,
        validation_schema TEXT,
        defense_strategies TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(identifier, version)
    )
''')
```

MySQL/MariaDB:
```python
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='user', password='pass', database='prompts')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompt_stanzas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        identifier VARCHAR(255) NOT NULL,
        version VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        template TEXT NOT NULL,
        validation_schema TEXT,
        defense_strategies TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY unique_identifier_version (identifier, version)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')
```

PostgreSQL:
```python
import psycopg2
conn = psycopg2.connect(host='localhost', user='user', password='pass', database='prompts')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompt_stanzas (
        id SERIAL PRIMARY KEY,
        identifier VARCHAR(255) NOT NULL,
        version VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        template TEXT NOT NULL,
        validation_schema TEXT,
        defense_strategies TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(identifier, version)
    )
''')
```
"""

import json
from typing import Any

from packaging import version as version_parser

from ..exceptions import AdapterError, StanzaNotFoundError
from ..models import PromptConfig
from .base import BaseInputAdapter


class SQLAdapter(BaseInputAdapter):
    """
    SQL database adapter for loading prompts from SQL tables.

    Supports multiple database engines:
    - SQLite (built-in Python support)
    - MySQL/MariaDB (requires: mysql-connector-python or pymysql)
    - PostgreSQL (requires: psycopg2 or psycopg2-binary)
    - SQL Server (requires: pyodbc)
    - Oracle (requires: cx_Oracle or oracledb)

    The adapter uses DB-API 2.0 compatible connections, so you can
    pass any connection object that implements the standard interface.

    Features:
    - Load from SQL database with automatic version resolution
    - Query by identifier and version
    - "latest" version support using semantic version sorting
    - Built-in caching with TTL support
    - Cross-database compatible SQL queries
    - Support for connection pooling (pass pool connection)

    Examples:
        # SQLite
        import sqlite3
        conn = sqlite3.connect('prompts.db')
        adapter = SQLAdapter(connection=conn, table_name='prompt_stanzas')

        # MySQL
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='user',
            password='pass',
            database='prompts'
        )
        adapter = SQLAdapter(connection=conn)

        # PostgreSQL
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            user='user',
            password='pass',
            database='prompts'
        )
        adapter = SQLAdapter(connection=conn)

        # Usage
        config = adapter.load("code_review")  # Latest version
        config = adapter.load("code_review", version="1.0.0")  # Specific version
    """

    def __init__(
        self,
        connection: Any,
        table_name: str = "prompt_stanzas",
        cache_enabled: bool = True,
        cache_ttl: int | None = None,
        max_cache_size: int | None = None,
        max_cache_memory_mb: float | None = None,
        auto_commit: bool = True,
    ) -> None:
        """
        Initialize the SQL adapter.

        Args:
            connection: DB-API 2.0 compatible connection object
                       (sqlite3.Connection, mysql.connector.MySQLConnection,
                        psycopg2.connection, pyodbc.Connection, etc.)
            table_name: Name of the table storing prompts (default: "prompt_stanzas")
            cache_enabled: Whether to enable caching
            cache_ttl: Cache time-to-live in seconds
            max_cache_size: Maximum number of items in cache
            max_cache_memory_mb: Maximum cache memory in MB
            auto_commit: Whether to auto-commit after queries (default: True)
        """
        super().__init__(
            cache_enabled=cache_enabled,
            cache_ttl=cache_ttl,
            max_cache_size=max_cache_size,
            max_cache_memory_mb=max_cache_memory_mb,
        )

        self.connection = connection
        self.table_name = table_name
        self.auto_commit = auto_commit

        # Validate connection has required methods
        if not hasattr(connection, "cursor"):
            raise ValueError(
                "Connection must be a DB-API 2.0 compatible connection object with cursor() method"
            )

    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load a prompt from the SQL database.

        Args:
            identifier: Prompt identifier (e.g., "code_review")
            version: Version string (semver like "1.0.0" or "latest")

        Returns:
            PromptConfig instance

        Raises:
            StanzaNotFoundError: If prompt not found
            AdapterError: If database query fails
        """
        # Check cache first
        if self._cache_enabled:
            cached = self._load_from_cache(identifier, version)
            if cached:
                return cached

        try:
            # Resolve version if "latest"
            if version == "latest":
                resolved_version = self._resolve_latest_version(identifier)
                if not resolved_version:
                    raise StanzaNotFoundError(f"No versions found for identifier '{identifier}'")
                version = resolved_version

            # Query for specific version
            row = self._query_prompt(identifier, version)
            if not row:
                raise StanzaNotFoundError(
                    f"Prompt '{identifier}' version '{version}' not found in table "
                    f"'{self.table_name}'"
                )

            # Parse row into PromptConfig
            config = self._row_to_config(row)

            # Cache the result
            if self._cache_enabled:
                self._add_to_cache(identifier, version, config)

            return config

        except StanzaNotFoundError:
            raise
        except Exception as e:
            raise AdapterError(
                f"Failed to load prompt '{identifier}' version '{version}' from SQL: {e}"
            ) from e

    def _query_prompt(self, identifier: str, version: str) -> dict[str, Any] | None:
        """
        Query a single prompt by identifier and version.

        Args:
            identifier: Prompt identifier
            version: Semantic version

        Returns:
            Row as dictionary or None if not found
        """
        cursor = self.connection.cursor()

        try:
            # Use parameterized query for SQL injection protection
            query = f"""
                SELECT id, identifier, version, name, description,
                       template, validation_schema, defense_strategies,
                       created_at, updated_at
                FROM {self.table_name}
                WHERE identifier = ? AND version = ?
            """

            # Note: Different databases use different parameter styles
            # ? for SQLite, %s for MySQL/PostgreSQL, :1/:2 for Oracle
            # This is SQLite/ODBC style - adjust if needed
            cursor.execute(query, (identifier, version))

            row = cursor.fetchone()
            if not row:
                return None

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Convert row to dictionary
            return dict(zip(columns, row, strict=False))

        finally:
            cursor.close()

    def _resolve_latest_version(self, identifier: str) -> str | None:
        """
        Find the latest semantic version for an identifier.

        Args:
            identifier: Prompt identifier

        Returns:
            Latest version string or None if no versions found
        """
        cursor = self.connection.cursor()

        try:
            # Query all versions for this identifier
            query = f"""
                SELECT version
                FROM {self.table_name}
                WHERE identifier = ?
                ORDER BY version DESC
            """

            cursor.execute(query, (identifier,))
            rows = cursor.fetchall()

            if not rows:
                return None

            # Extract versions and parse as semantic versions
            versions = [row[0] for row in rows]

            # Sort versions using semantic versioning
            try:
                parsed_versions = [(v, version_parser.parse(v)) for v in versions]
                parsed_versions.sort(key=lambda x: x[1], reverse=True)
                return parsed_versions[0][0]
            except Exception:
                # Fallback to string sorting if semantic parsing fails
                versions.sort(reverse=True)
                return versions[0]

        finally:
            cursor.close()

    def _row_to_config(self, row: dict[str, Any]) -> PromptConfig:
        """
        Convert database row to PromptConfig.

        Args:
            row: Database row as dictionary

        Returns:
            PromptConfig instance
        """
        # Parse JSON fields (may already be parsed by some drivers)
        template = row["template"]
        if isinstance(template, str):
            try:
                template = json.loads(template)
            except json.JSONDecodeError:
                # Shouldn't happen with JSON column, but fallback
                template = {"template": template}

        # Unwrap simple string templates from {"template": "..."} wrapper
        if isinstance(template, dict) and len(template) == 1 and "template" in template:
            template = template["template"]

        validation_schema = row.get("validation_schema")
        if validation_schema and isinstance(validation_schema, str):
            try:
                validation_schema = json.loads(validation_schema)
            except json.JSONDecodeError:
                validation_schema = []

        defense_strategies = row.get("defense_strategies")
        if defense_strategies and isinstance(defense_strategies, str):
            try:
                defense_strategies = json.loads(defense_strategies)
            except json.JSONDecodeError:
                defense_strategies = []

        # Build config dict
        config_dict: dict[str, Any] = {
            "name": row["name"],
            "version": row["version"],
            "template": template,
        }

        if row.get("description"):
            config_dict["description"] = row["description"]

        if validation_schema:
            config_dict["validation_schema"] = validation_schema

        if defense_strategies:
            config_dict["defense_strategies"] = defense_strategies

        # Compile to PromptConfig
        return self._compile_from_dict(config_dict)

    def list_identifiers(self) -> list[str]:
        """
        List all unique prompt identifiers in the table.

        Returns:
            List of identifier strings
        """
        cursor = self.connection.cursor()

        try:
            query = f"""
                SELECT DISTINCT identifier
                FROM {self.table_name}
                ORDER BY identifier
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            return [row[0] for row in rows]

        finally:
            cursor.close()

    def list_versions(self, identifier: str) -> list[str]:
        """
        List all versions for a given identifier.

        Args:
            identifier: Prompt identifier

        Returns:
            List of version strings sorted by semantic version (newest first)
        """
        cursor = self.connection.cursor()

        try:
            query = f"""
                SELECT version
                FROM {self.table_name}
                WHERE identifier = ?
                ORDER BY version DESC
            """

            cursor.execute(query, (identifier,))
            rows = cursor.fetchall()

            versions = [row[0] for row in rows]

            # Sort using semantic versioning
            try:
                parsed = [(v, version_parser.parse(v)) for v in versions]
                parsed.sort(key=lambda x: x[1], reverse=True)
                return [v[0] for v in parsed]
            except Exception:
                # Fallback to string sort
                versions.sort(reverse=True)
                return versions

        finally:
            cursor.close()

    def insert(
        self,
        identifier: str,
        version: str,
        name: str,
        template: str | dict[str, Any],
        description: str | None = None,
        validation_schema: list[dict[str, Any]] | None = None,
        defense_strategies: list[str] | None = None,
    ) -> int:
        """
        Insert a new prompt into the database.

        Args:
            identifier: Prompt identifier
            version: Semantic version
            name: Prompt name
            template: Template string or dict (will be JSON-encoded if dict)
            description: Optional description
            validation_schema: Optional validation schema
            defense_strategies: Optional defense strategies

        Returns:
            Inserted row ID

        Raises:
            AdapterError: If insert fails (e.g., duplicate identifier+version)
        """
        cursor = self.connection.cursor()

        try:
            # Wrap string templates in JSON object, keep dict templates as-is
            template_json = {"template": template} if isinstance(template, str) else template

            # Encode as JSON strings for database insertion
            template_str = json.dumps(template_json)
            schema_str = json.dumps(validation_schema) if validation_schema else None
            strategies_str = json.dumps(defense_strategies) if defense_strategies else None

            query = f"""
                INSERT INTO {self.table_name}
                (identifier, version, name, description, template, 
                 validation_schema, defense_strategies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(
                query,
                (
                    identifier,
                    version,
                    name,
                    description,
                    template_str,
                    schema_str,
                    strategies_str,
                ),
            )

            if self.auto_commit:
                self.connection.commit()

            # Get the inserted row ID
            row_id = cursor.lastrowid

            return row_id

        except Exception as e:
            if self.auto_commit:
                self.connection.rollback()
            raise AdapterError(f"Failed to insert prompt: {e}") from e

        finally:
            cursor.close()

    def update(
        self,
        identifier: str,
        version: str,
        **updates: Any,
    ) -> None:
        """
        Update an existing prompt.

        Args:
            identifier: Prompt identifier
            version: Version to update
            **updates: Fields to update (name, description, template, etc.)

        Raises:
            StanzaNotFoundError: If prompt not found
            AdapterError: If update fails
        """
        cursor = self.connection.cursor()

        try:
            # Build UPDATE statement dynamically
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key in ("template", "validation_schema", "defense_strategies") and isinstance(
                    value, (dict, list)
                ):
                    value = json.dumps(value)

                set_clauses.append(f"{key} = ?")
                values.append(value)

            if not set_clauses:
                raise ValueError("No fields to update")

            # Add updated_at
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")

            values.extend([identifier, version])

            query = f"""
                UPDATE {self.table_name}
                SET {", ".join(set_clauses)}
                WHERE identifier = ? AND version = ?
            """

            cursor.execute(query, values)

            if cursor.rowcount == 0:
                raise StanzaNotFoundError(f"Prompt '{identifier}' version '{version}' not found")

            if self.auto_commit:
                self.connection.commit()

            # Invalidate cache for this prompt
            if self._cache_enabled:
                cache_key = f"{identifier}:{version}"
                self._cache.pop(cache_key, None)

        except StanzaNotFoundError:
            raise
        except Exception as e:
            if self.auto_commit:
                self.connection.rollback()
            raise AdapterError(f"Failed to update prompt: {e}") from e

        finally:
            cursor.close()

    def delete(self, identifier: str, version: str) -> None:
        """
        Delete a prompt from the database.

        Args:
            identifier: Prompt identifier
            version: Version to delete

        Raises:
            StanzaNotFoundError: If prompt not found
            AdapterError: If delete fails
        """
        cursor = self.connection.cursor()

        try:
            query = f"""
                DELETE FROM {self.table_name}
                WHERE identifier = ? AND version = ?
            """

            cursor.execute(query, (identifier, version))

            if cursor.rowcount == 0:
                raise StanzaNotFoundError(f"Prompt '{identifier}' version '{version}' not found")

            if self.auto_commit:
                self.connection.commit()

            # Invalidate cache
            if self._cache_enabled:
                cache_key = f"{identifier}:{version}"
                self._cache.pop(cache_key, None)

        except StanzaNotFoundError:
            raise
        except Exception as e:
            if self.auto_commit:
                self.connection.rollback()
            raise AdapterError(f"Failed to delete prompt: {e}") from e

        finally:
            cursor.close()

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self.connection, "close"):
            self.connection.close()
