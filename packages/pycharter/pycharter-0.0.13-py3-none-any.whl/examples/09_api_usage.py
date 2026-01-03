#!/usr/bin/env python3
"""
Example: Using PyCharter API

This example demonstrates how to use the PyCharter REST API endpoints.
Make sure the API server is running: pycharter api
"""

import json
import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


def example_parse_contract():
    """Example: Parse a contract via API."""
    print("=" * 70)
    print("Example: Parse Contract via API")
    print("=" * 70)
    
    contract_data = {
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            },
            "required": ["name", "age"]
        },
        "metadata": {
            "title": "User Contract",
            "version": "1.0.0",
            "description": "User data contract"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/contracts/parse",
        json={"contract": contract_data}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Contract parsed successfully")
        print(f"  Schema properties: {len(result.get('schema', {}).get('properties', {}))}")
        print(f"  Metadata title: {result.get('metadata', {}).get('title')}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.json()}")


def example_store_schema():
    """Example: Store a schema via API."""
    print("\n" + "=" * 70)
    print("Example: Store Schema via API")
    print("=" * 70)
    
    schema_data = {
        "schema_name": "user_schema",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        },
        "version": "1.0.0"
    }
    
    response = requests.post(
        f"{BASE_URL}/metadata/schemas",
        json=schema_data
    )
    
    if response.status_code == 201:
        result = response.json()
        print("✓ Schema stored successfully")
        print(f"  Schema ID: {result.get('schema_id')}")
        return result.get('schema_id')
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.json()}")
        return None


def example_validate_data(schema_id: str):
    """Example: Validate data via API."""
    print("\n" + "=" * 70)
    print("Example: Validate Data via API")
    print("=" * 70)
    
    validation_data = {
        "schema_id": schema_id,
        "data": {
            "name": "Alice",
            "age": 30
        },
        "strict": False
    }
    
    response = requests.post(
        f"{BASE_URL}/validation/validate",
        json=validation_data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('is_valid'):
            print("✓ Data validated successfully")
            print(f"  Validated data: {result.get('data')}")
        else:
            print("✗ Validation failed")
            print(f"  Errors: {result.get('errors')}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.json()}")


def example_generate_schema():
    """Example: Generate Pydantic model from JSON Schema via API."""
    print("\n" + "=" * 70)
    print("Example: Generate Schema via API")
    print("=" * 70)
    
    generate_data = {
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name", "age"]
        },
        "model_name": "User"
    }
    
    response = requests.post(
        f"{BASE_URL}/schemas/generate",
        json=generate_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Model generated successfully")
        print(f"  Model name: {result.get('model_name')}")
        print(f"  Schema properties: {len(result.get('schema_json', {}).get('properties', {}))}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.json()}")


def main():
    """Run all API examples."""
    print("\n" + "=" * 70)
    print("PyCharter API Usage Examples")
    print("=" * 70)
    print("\nMake sure the API server is running:")
    print("  pycharter api")
    print("  or")
    print("  uvicorn api.main:app --reload")
    print()
    
    try:
        # Test API is running
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("⚠️  API server may not be running. Please start it first.")
            return
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to API server at http://localhost:8000")
        print("   Please start the server: pycharter api")
        return
    
    # Run examples
    example_parse_contract()
    schema_id = example_store_schema()
    if schema_id:
        example_validate_data(schema_id)
    example_generate_schema()
    
    print("\n" + "=" * 70)
    print("✓ All examples completed")
    print("=" * 70)
    print("\nView API documentation at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()

