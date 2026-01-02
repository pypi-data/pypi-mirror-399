"""Utility to create DynamoDB table for prompt stanzas."""


def create_dynamodb_table(
    table_name: str = "prompt-stanzas",
    region_name: str | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    endpoint_url: str | None = None,
    billing_mode: str = "PAY_PER_REQUEST",
) -> dict:
    """
    Create a DynamoDB table for storing prompt stanzas.

    Table Schema:
    - Partition Key: identifier (String)
    - Sort Key: version (String)
    - Billing Mode: PAY_PER_REQUEST (on-demand) or PROVISIONED

    Args:
        table_name: Name of the table to create
        region_name: AWS region name
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        endpoint_url: Custom endpoint URL (for local DynamoDB)
        billing_mode: "PAY_PER_REQUEST" or "PROVISIONED"

    Returns:
        Table creation response from DynamoDB

    Raises:
        ImportError: If boto3 is not installed
        Exception: If table creation fails

    Example:
        >>> create_dynamodb_table(
        ...     table_name="prompt-stanzas",
        ...     region_name="us-east-1"
        ... )
    """
    try:
        import boto3
    except ImportError as e:
        raise ImportError("boto3 is required. Install it with: pip install boto3") from e

    # Initialize DynamoDB client
    session_config = {}
    if region_name:
        session_config["region_name"] = region_name
    if aws_access_key_id:
        session_config["aws_access_key_id"] = aws_access_key_id
    if aws_secret_access_key:
        session_config["aws_secret_access_key"] = aws_secret_access_key

    dynamodb = boto3.client("dynamodb", endpoint_url=endpoint_url, **session_config)

    # Define table schema
    table_config = {
        "TableName": table_name,
        "KeySchema": [
            {"AttributeName": "identifier", "KeyType": "HASH"},  # Partition key
            {"AttributeName": "version", "KeyType": "RANGE"},  # Sort key
        ],
        "AttributeDefinitions": [
            {"AttributeName": "identifier", "AttributeType": "S"},
            {"AttributeName": "version", "AttributeType": "S"},
        ],
        "BillingMode": billing_mode,
    }

    # Add provisioned throughput if needed
    if billing_mode == "PROVISIONED":
        table_config["ProvisionedThroughput"] = {
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        }

    # Create table
    try:
        response = dynamodb.create_table(**table_config)
        print(f"✓ DynamoDB table '{table_name}' created successfully")
        print(f"  Status: {response['TableDescription']['TableStatus']}")
        print(f"  ARN: {response['TableDescription']['TableArn']}")
        return response
    except dynamodb.exceptions.ResourceInUseException:
        print(f"✓ DynamoDB table '{table_name}' already exists")
        return {"status": "already_exists"}
    except Exception as e:
        print(f"✗ Failed to create DynamoDB table '{table_name}': {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create DynamoDB table for prompt stanzas")
    parser.add_argument(
        "--table-name",
        default="prompt-stanzas",
        help="Name of the DynamoDB table (default: prompt-stanzas)",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWS region name (default: from AWS config)",
    )
    parser.add_argument(
        "--endpoint-url",
        default=None,
        help="Custom endpoint URL (for local DynamoDB)",
    )
    parser.add_argument(
        "--billing-mode",
        default="PAY_PER_REQUEST",
        choices=["PAY_PER_REQUEST", "PROVISIONED"],
        help="Billing mode (default: PAY_PER_REQUEST)",
    )

    args = parser.parse_args()

    create_dynamodb_table(
        table_name=args.table_name,
        region_name=args.region,
        endpoint_url=args.endpoint_url,
        billing_mode=args.billing_mode,
    )
