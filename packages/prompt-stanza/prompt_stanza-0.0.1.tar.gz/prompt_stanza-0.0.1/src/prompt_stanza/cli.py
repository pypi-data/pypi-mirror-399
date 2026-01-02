"""Command-line interface for Prompt Stanza."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_examples(example: str | None = None) -> None:
    """Run examples in the examples directory.

    Args:
        example: Optional specific example file to run (e.g., 'basic_example.py')
                 If None, runs all examples.
    """
    print("=" * 60)
    if example:
        print(f"Running Example: {example}")
    else:
        print("Running Prompt Stanza Examples")
    print("=" * 60)
    print()

    # Find examples directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    examples_dir = project_root / "examples"

    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir}")
        sys.exit(1)

    # If specific example requested, run it directly
    if example:
        # Try to find the example file
        example_file = None
        for subdir in ["basic", "advanced", "input_adapters", "output_adapters"]:
            potential_path = examples_dir / subdir / example
            if potential_path.exists():
                example_file = potential_path
                break

        if not example_file:
            print(f"❌ Example not found: {example}")
            print()
            print("Available examples:")
            print("  Basic:")
            for f in (examples_dir / "basic").glob("*.py"):
                if f.name != "__init__.py":
                    print(f"    - {f.name}")
            print("  Advanced:")
            for f in (examples_dir / "advanced").glob("*.py"):
                if f.name != "__init__.py":
                    print(f"    - {f.name}")
            sys.exit(1)

        print(f"✓ Found example: {example_file}")
        print()
        try:
            # Run with uv if available, otherwise python
            try:
                subprocess.run(["uv", "run", "python", str(example_file)], check=True)
            except FileNotFoundError:
                subprocess.run(["python", str(example_file)], check=True)
            print()
            print(f"✓ Example '{example}' completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Example failed with exit code {e.returncode}")
            sys.exit(e.returncode)
    else:
        # Run the examples shell script
        run_script = examples_dir / "run_examples.sh"
        if run_script.exists():
            print(f"✓ Found examples runner: {run_script}")
            print()
            try:
                subprocess.run(["bash", str(run_script)], check=True)
                print()
                print("✓ All examples completed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Examples failed with exit code {e.returncode}")
                sys.exit(e.returncode)
        else:
            print(f"❌ Examples runner script not found: {run_script}")
            sys.exit(1)


def create_dynamodb_table(
    table_name: str = "prompt-stanzas",
    region: str | None = None,
    endpoint_url: str | None = None,
    billing_mode: str = "PAY_PER_REQUEST",
) -> None:
    """Create a DynamoDB table for prompt stanzas."""
    print("=" * 60)
    print("Creating DynamoDB Table")
    print("=" * 60)
    print()

    try:
        from prompt_stanza.utils import create_dynamodb_table as create_table
    except ImportError:
        print("❌ boto3 is required to create DynamoDB tables.")
        print("   Install with: pip install prompt-stanza[aws]")
        sys.exit(1)

    print(f"Table name: {table_name}")
    print(f"Region: {region or 'default from AWS config'}")
    print(f"Billing mode: {billing_mode}")
    if endpoint_url:
        print(f"Endpoint URL: {endpoint_url}")
    print()

    try:
        result = create_table(
            table_name=table_name,
            region_name=region,
            endpoint_url=endpoint_url,
            billing_mode=billing_mode,
        )
        print()
        print("✓ DynamoDB table setup complete")
        if isinstance(result, dict) and result.get("status") == "already_exists":
            print("  (Table already existed)")
    except Exception as e:
        print(f"❌ Failed to create DynamoDB table: {e}")
        sys.exit(1)


def create_mongodb_collection(
    connection_string: str = "mongodb://localhost:27017/",
    database: str = "prompts",
    collection: str = "prompt_stanzas",
    create_indexes: bool = True,
    add_validation: bool = True,
) -> None:
    """Create a MongoDB collection for prompt stanzas."""
    print("=" * 60)
    print("Creating MongoDB Collection")
    print("=" * 60)
    print()

    try:
        from prompt_stanza.utils import setup_mongodb_collection
    except ImportError:
        print("❌ pymongo is required to create MongoDB collections.")
        print("   Install with: pip install prompt-stanza[mongodb]")
        sys.exit(1)

    print(f"Connection: {connection_string}")
    print(f"Database: {database}")
    print(f"Collection: {collection}")
    print(f"Create indexes: {create_indexes}")
    print(f"Add validation: {add_validation}")
    print()

    try:
        result = setup_mongodb_collection(
            connection_string=connection_string,
            database_name=database,
            collection_name=collection,
            create_indexes=create_indexes,
            add_validation=add_validation,
        )
        print()
        print("✓ MongoDB collection setup complete")
        print(f"  Collection: {result.get('collection')}")
        print(f"  Indexes: {result.get('indexes_created', 0)} created")
    except Exception as e:
        print(f"❌ Failed to create MongoDB collection: {e}")
        sys.exit(1)


def create_sql_table(
    database_type: str = "sqlite",
    connection_string: str | None = None,
    output_file: str | None = None,
) -> None:
    """Create a SQL table for prompt stanzas or output DDL."""
    print("=" * 60)
    print("Creating SQL Table")
    print("=" * 60)
    print()

    # Import DDL statements
    try:
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        examples_dir = project_root / "examples" / "input_adapters"

        # Read the DDL file
        ddl_file = examples_dir / "sql_adapter_ddl.py"
        if not ddl_file.exists():
            print(f"❌ DDL file not found: {ddl_file}")
            sys.exit(1)

        # Import DDL constants
        import importlib.util

        spec = importlib.util.spec_from_file_location("sql_ddl", ddl_file)
        sql_ddl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sql_ddl)

        ddl_mapping = {
            "sqlite": sql_ddl.SQLITE_DDL,
            "mysql": sql_ddl.MYSQL_DDL,
            "postgresql": sql_ddl.POSTGRESQL_DDL,
            "postgres": sql_ddl.POSTGRESQL_DDL,
            "oracle": sql_ddl.ORACLE_DDL,
            "sqlserver": sql_ddl.SQL_SERVER_DDL,
            "mssql": sql_ddl.SQL_SERVER_DDL,
        }

        if database_type.lower() not in ddl_mapping:
            print(f"❌ Unsupported database type: {database_type}")
            print(f"   Supported types: {', '.join(ddl_mapping.keys())}")
            sys.exit(1)

        ddl = ddl_mapping[database_type.lower()]

        # Output DDL or execute
        if output_file:
            # Write DDL to file
            output_path = Path(output_file)
            output_path.write_text(ddl)
            print(f"✓ DDL written to: {output_path}")
        elif connection_string:
            # Execute DDL
            print(f"Database type: {database_type}")
            print(f"Connection: {connection_string}")
            print()

            if database_type.lower() == "sqlite":
                import sqlite3

                conn = sqlite3.connect(connection_string)
                conn.executescript(ddl)
                conn.commit()
                conn.close()
                print("✓ SQLite table created successfully")
            elif database_type.lower() in ["mysql", "mariadb"]:
                try:
                    from urllib.parse import urlparse

                    import mysql.connector

                    # Parse connection string (mysql://user:pass@host:port/database)
                    parsed = urlparse(connection_string)
                    conn_params = {
                        "host": parsed.hostname or "localhost",
                        "user": parsed.username or "root",
                        "database": parsed.path.lstrip("/") if parsed.path else None,
                    }
                    if parsed.password:
                        conn_params["password"] = parsed.password
                    if parsed.port:
                        conn_params["port"] = parsed.port

                    conn = mysql.connector.connect(**conn_params)
                    cursor = conn.cursor()
                    cursor.execute(ddl)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    print("✓ MySQL table created successfully")
                except ImportError:
                    print("❌ mysql-connector-python is required")
                    print("   Install with: pip install mysql-connector-python")
                    sys.exit(1)
            elif database_type.lower() in ["postgresql", "postgres"]:
                try:
                    import psycopg2

                    conn = psycopg2.connect(connection_string)
                    cursor = conn.cursor()
                    cursor.execute(ddl)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    print("✓ PostgreSQL table created successfully")
                except ImportError:
                    print("❌ psycopg2 is required for PostgreSQL")
                    print("   Install with: pip install prompt-stanza[sql]")
                    sys.exit(1)
            else:
                print(f"❌ Direct execution not supported for {database_type}")
                print("   Use --output-file to generate DDL instead")
                sys.exit(1)
        else:
            # Just print DDL
            print(f"DDL for {database_type}:")
            print()
            print(ddl)
            print()
            print("Use --connection-string to execute or --output-file to save")

    except Exception as e:
        print(f"❌ Failed to create SQL table: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def create_template(
    format_type: str,
    output_file: str,
    name: str = "my_prompt",
    version: str = "1.0.0",
    description: str = "A sample prompt template",
) -> None:
    """Create a sample prompt template in YAML or JSON format."""
    print("=" * 60)
    print(f"Creating {format_type.upper()} Template")
    print("=" * 60)
    print()

    # Sample template structure matching the code_review example format
    template_data = {
        "name": name,
        "version": version,
        "description": description,
        "defense_strategies": [],
        "template": {
            "system": "You are a helpful assistant specialized in {{ domain }}.",
            "task": "{{ task_description }}",
            "output_format": "Provide your response in a clear and structured format.",
            "use_sandwich_defense": False,
            "delimiting_strategy": "xml",
        },
        "validation_schema": [
            {"name": "domain", "type": "str", "description": "The domain or specialty area"},
            {
                "name": "task_description",
                "type": "str",
                "description": "Description of the task to complete",
            },
        ],
    }

    output_path = Path(output_file)

    try:
        if format_type == "yaml" or format_type == "yml":
            import yaml

            with open(output_path, "w") as f:
                yaml.dump(template_data, f, default_flow_style=False, sort_keys=False)
            print(f"✓ YAML template created: {output_path}")
        elif format_type == "json":
            with open(output_path, "w") as f:
                json.dump(template_data, f, indent=2)
            print(f"✓ JSON template created: {output_path}")
        else:
            print(f"❌ Unsupported format: {format_type}")
            print("   Supported formats: yaml, yml, json")
            sys.exit(1)

        print()
        print("Template structure:")
        print(f"  Name: {name}")
        print(f"  Version: {version}")
        print(f"  Description: {description}")
        print()
        print("Edit the file to customize your prompt template.")

    except ImportError as e:
        if "yaml" in str(e).lower():
            print("❌ PyYAML is required for YAML templates")
            print("   Install with: pip install pyyaml")
        else:
            print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to create template: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Prompt Stanza CLI - Manage prompts, databases, and examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all examples
  prompt-stanza run-examples
  
  # Run specific example
  prompt-stanza run-examples --example basic_example.py
  prompt-stanza run-examples --example ab_testing_example.py
  
  # Create database tables/collections
  prompt-stanza create-dynamodb-table --table-name my-prompts --region us-east-1
  prompt-stanza create-mongodb-collection --database prompts --collection stanzas
  prompt-stanza create-sql-table --type sqlite --connection-string prompts.db
  
  # Create templates
  prompt-stanza create-template yaml --output my_prompt.yaml
  prompt-stanza create-template json --output my_prompt.json --name "code_review"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run examples command
    run_examples_parser = subparsers.add_parser("run-examples", help="Run example scripts")
    run_examples_parser.add_argument(
        "--example",
        help=(
            "Specific example file to run (e.g., basic_example.py, ab_testing_example.py). "
            "If not specified, runs all examples."
        ),
    )

    # Create DynamoDB table command
    dynamo_parser = subparsers.add_parser(
        "create-dynamodb-table", help="Create a DynamoDB table for prompt stanzas"
    )
    dynamo_parser.add_argument(
        "--table-name",
        default="prompt-stanzas",
        help="Name of the DynamoDB table (default: prompt-stanzas)",
    )
    dynamo_parser.add_argument("--region", help="AWS region name (default: from AWS config)")
    dynamo_parser.add_argument("--endpoint-url", help="Custom endpoint URL (for local DynamoDB)")
    dynamo_parser.add_argument(
        "--billing-mode",
        choices=["PAY_PER_REQUEST", "PROVISIONED"],
        default="PAY_PER_REQUEST",
        help="Billing mode (default: PAY_PER_REQUEST)",
    )

    # Create MongoDB collection command
    mongo_parser = subparsers.add_parser(
        "create-mongodb-collection", help="Create a MongoDB collection for prompt stanzas"
    )
    mongo_parser.add_argument(
        "--connection-string",
        default="mongodb://localhost:27017/",
        help="MongoDB connection string (default: mongodb://localhost:27017/)",
    )
    mongo_parser.add_argument(
        "--database", default="prompts", help="Database name (default: prompts)"
    )
    mongo_parser.add_argument(
        "--collection", default="prompt_stanzas", help="Collection name (default: prompt_stanzas)"
    )
    mongo_parser.add_argument("--no-indexes", action="store_true", help="Skip creating indexes")
    mongo_parser.add_argument(
        "--no-validation", action="store_true", help="Skip adding validation schema"
    )

    # Create SQL table command
    sql_parser = subparsers.add_parser(
        "create-sql-table", help="Create a SQL table for prompt stanzas"
    )
    sql_parser.add_argument(
        "--type",
        required=True,
        choices=["sqlite", "mysql", "postgresql", "postgres", "oracle", "sqlserver", "mssql"],
        help="Database type",
    )
    sql_parser.add_argument(
        "--connection-string", help="Database connection string (for direct execution)"
    )
    sql_parser.add_argument("--output-file", help="Output DDL to file instead of executing")

    # Create template command
    template_parser = subparsers.add_parser(
        "create-template", help="Create a sample prompt template"
    )
    template_parser.add_argument("format", choices=["yaml", "yml", "json"], help="Template format")
    template_parser.add_argument("--output", required=True, help="Output file path")
    template_parser.add_argument(
        "--name", default="my_prompt", help="Template name (default: my_prompt)"
    )
    template_parser.add_argument(
        "--version", default="1.0.0", help="Template version (default: 1.0.0)"
    )
    template_parser.add_argument(
        "--description", default="A sample prompt template", help="Template description"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute commands
    if args.command == "run-examples":
        run_examples(example=args.example)
    elif args.command == "create-dynamodb-table":
        create_dynamodb_table(
            table_name=args.table_name,
            region=args.region,
            endpoint_url=args.endpoint_url,
            billing_mode=args.billing_mode,
        )
    elif args.command == "create-mongodb-collection":
        create_mongodb_collection(
            connection_string=args.connection_string,
            database=args.database,
            collection=args.collection,
            create_indexes=not args.no_indexes,
            add_validation=not args.no_validation,
        )
    elif args.command == "create-sql-table":
        create_sql_table(
            database_type=args.type,
            connection_string=args.connection_string,
            output_file=args.output_file,
        )
    elif args.command == "create-template":
        create_template(
            format_type=args.format,
            output_file=args.output,
            name=args.name,
            version=args.version,
            description=args.description,
        )


if __name__ == "__main__":
    main()
