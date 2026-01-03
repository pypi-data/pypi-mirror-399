#!/usr/bin/env python3
"""
Example 2: Metadata Store Client

Demonstrates how to store and retrieve metadata components using different
metadata store implementations:
- InMemoryMetadataStore (for testing/development)
- PostgresMetadataStore (for production with PostgreSQL)
- MongoDBMetadataStore (for production with MongoDB)
- RedisMetadataStore (for high-throughput scenarios)

This example shows how to use built-in implementations and how to create
custom implementations by subclassing MetadataStoreClient.
"""

from pathlib import Path

from pycharter import (
    MetadataStoreClient,
    InMemoryMetadataStore,
    parse_contract_file,
)

# Optional imports for database-backed stores
try:
    from pycharter import PostgresMetadataStore, MongoDBMetadataStore, RedisMetadataStore
except ImportError:
    PostgresMetadataStore = None
    MongoDBMetadataStore = None
    RedisMetadataStore = None


class ExampleMetadataStore(MetadataStoreClient):
    """
    Example implementation of MetadataStoreClient.
    
    In production, you would implement actual database operations here.
    This example uses in-memory storage for demonstration.
    """
    
    def __init__(self, connection_string: str = None):
        super().__init__(connection_string)
        # In-memory storage for demonstration
        self._schemas = {}
        self._governance_rules = {}
        self._ownership = {}
        self._metadata = {}
        self._next_id = 1
    
    def connect(self):
        """Establish connection (mock for this example)."""
        print("  ✓ Connected to metadata store")
        self._connection = "connected"
    
    def disconnect(self):
        """Close connection."""
        self._connection = None
        print("  ✓ Disconnected from metadata store")
    
    def store_schema(self, schema_name: str, schema: dict, version: str = None):
        """Store a schema."""
        schema_id = self._next_id
        self._next_id += 1
        key = f"{schema_name}:{version}" if version else schema_name
        self._schemas[schema_id] = {
            "id": schema_id,
            "name": schema_name,
            "version": version,
            "schema": schema,
        }
        print(f"  ✓ Stored schema '{schema_name}' (ID: {schema_id}, Version: {version})")
        return schema_id
    
    def get_schema(self, schema_id: int):
        """Retrieve a schema."""
        if schema_id in self._schemas:
            return self._schemas[schema_id]["schema"]
        return None
    


def example_store_metadata():
    """Demonstrate storing metadata from a parsed contract."""
    print("=" * 70)
    print("Example 2a: Storing Metadata from Parsed Contract")
    print("=" * 70)
    
    # Parse a contract
    contract_path = Path(__file__).parent.parent / "data" / "contracts" / "user_contract.yaml"
    if contract_path.exists():
        metadata = parse_contract_file(str(contract_path))
    else:
        # Use inline contract as fallback (ownership and governance_rules nested in metadata)
        print("  ⚠ Contract file not found, using inline contract...")
        contract_dict = {
            "schema": {
                "type": "object",
                "version": "1.0.0",
                "properties": {
                    "user_id": {"type": "string"},
                    "username": {"type": "string", "minLength": 3},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["user_id", "username", "email"]
            },
            "metadata": {
                "version": "1.0.0",
                "description": "User contract",
                "ownership": {"owner": "data-team", "team": "engineering"},
                "governance_rules": {"data_retention": {"days": 365}}
            }
        }
        metadata = parse_contract(contract_dict)
    
    # Create and connect to metadata store
    store = ExampleMetadataStore(connection_string="example://database")
    store.connect()
    
    try:
        # Store schema
        schema_id = store.store_schema(
            schema_name="user",
            schema=metadata.schema,
            version=metadata.metadata.get("version", "1.0.0"),
        )
        
        # Merge ownership and governance rules into metadata before storing
        # Ownership and governance are part of metadata, not separate entities
        metadata_dict = metadata.metadata.copy() if metadata.metadata else {}
        
        if metadata.ownership:
            metadata_dict["business_owners"] = [metadata.ownership.get("owner", "unknown")] if metadata.ownership.get("owner") else []
        
        if metadata.governance_rules:
            metadata_dict["governance_rules"] = metadata.governance_rules
        
        # Store metadata once with all information (ownership and governance included)
        store.store_metadata(
            resource_id=schema_id,
            resource_type="schema",
            metadata=metadata_dict,
        )
        
        print(f"\n✓ All metadata components stored for schema ID: {schema_id}")
        
        return store, schema_id
    
    finally:
        store.disconnect()


def example_retrieve_metadata():
    """Demonstrate retrieving stored metadata."""
    print("\n" + "=" * 70)
    print("Example 2b: Retrieving Stored Metadata")
    print("=" * 70)
    
    # Store some metadata first
    store = ExampleMetadataStore()
    store.connect()
    
    try:
        # Store a schema
        schema_id = store.store_schema(
            schema_name="product",
            schema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                },
            },
            version="1.0.0",
        )
        
        # Retrieve the schema
        stored_schema = store.get_schema(schema_id)
        
        if stored_schema:
            print(f"\n✓ Retrieved schema (ID: {schema_id})")
            print(f"  Properties: {list(stored_schema.get('properties', {}).keys())}")
        else:
            print(f"\n✗ Schema not found (ID: {schema_id})")
    
    finally:
        store.disconnect()


def example_all_store_implementations():
    """Demonstrate all available store implementations."""
    print("\n" + "=" * 70)
    print("Example 2c: All Available Store Implementations")
    print("=" * 70)
    
    print("\n1. InMemoryMetadataStore (Always Available)")
    print("-" * 70)
    print("  Use for: Testing, development, prototyping")
    print("  Dependencies: None")
    print("  Example:")
    print("    store = InMemoryMetadataStore()")
    print("    store.connect()")
    print("    schema_id = store.store_schema('user', schema, version='1.0.0')")
    
    if PostgresMetadataStore:
        print("\n2. PostgresMetadataStore (Requires psycopg2-binary)")
        print("-" * 70)
        print("  Use for: Production systems, ACID transactions, complex queries")
        print("  Dependencies: psycopg2-binary")
        print("  Initialization: pycharter db init <connection_string>")
        print("  Example:")
        print("    store = PostgresMetadataStore(")
        print("        connection_string='postgresql://user:pass@localhost/pycharter'")
        print("    )")
        print("    store.connect()  # Requires: pycharter db init first")
        print("    schema_id = store.store_schema('user', schema, version='1.0.0')")
    else:
        print("\n2. PostgresMetadataStore (Not Available)")
        print("-" * 70)
        print("  Install with: pip install psycopg2-binary")
    
    if MongoDBMetadataStore:
        print("\n3. MongoDBMetadataStore (Requires pymongo)")
        print("-" * 70)
        print("  Use for: Flexible schema, document storage, rapid development")
        print("  Dependencies: pymongo")
        print("  Initialization: Auto-creates indexes on first connection")
        print("  Example:")
        print("    store = MongoDBMetadataStore(")
        print("        connection_string='mongodb://user:pass@localhost:27017/',")
        print("        database_name='pycharter'")
        print("    )")
        print("    store.connect()  # Auto-initializes")
        print("    schema_id = store.store_schema('user', schema, version='1.0.0')")
    else:
        print("\n3. MongoDBMetadataStore (Not Available)")
        print("-" * 70)
        print("  Install with: pip install pymongo")
    
    if RedisMetadataStore:
        print("\n4. RedisMetadataStore (Requires redis)")
        print("-" * 70)
        print("  Use for: High-throughput, caching, ephemeral data")
        print("  Dependencies: redis")
        print("  Example:")
        print("    store = RedisMetadataStore(")
        print("        connection_string='redis://localhost:6379/0'")
        print("    )")
        print("    store.connect()")
        print("    schema_id = store.store_schema('user', schema, version='1.0.0')")
    else:
        print("\n4. RedisMetadataStore (Not Available)")
        print("-" * 70)
        print("  Install with: pip install redis")


def example_custom_implementation():
    """Show how to create a custom implementation."""
    print("\n" + "=" * 70)
    print("Example 2d: Custom Database Implementation")
    print("=" * 70)
    
    print("""
To implement for your database, subclass MetadataStoreClient:

```python
import json
from pycharter import MetadataStoreClient

class CustomMetadataStore(MetadataStoreClient):
    def connect(self):
        # Establish your database connection
        self._connection = your_database.connect(self.connection_string)
    
    def store_schema(self, schema_name: str, schema: dict, version: str = None):
        # Implement schema storage logic
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO schemas (name, version, schema_json) VALUES (?, ?, ?) RETURNING id",
            (schema_name, version, json.dumps(schema))
        )
        return cursor.fetchone()[0]
    
    def get_schema(self, schema_id: int):
        # Implement schema retrieval logic
        cursor = self._connection.cursor()
        cursor.execute("SELECT schema_json FROM schemas WHERE id = ?", (schema_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None
    
    # Implement other required methods:
    # - store_metadata()
    # - get_metadata()
    # - store_coercion_rules()
    # - get_coercion_rules()
    # - store_validation_rules()
    # - get_validation_rules()
    # - disconnect()
```

Then use it:
```python
store = CustomMetadataStore(connection_string="your://connection/string")
store.connect()
schema_id = store.store_schema("user", schema_dict, version="1.0.0")
```
""")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Metadata Store Service Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    try:
        store, schema_id = example_store_metadata()
    except FileNotFoundError:
        print("⚠ Contract file not found, skipping example 2a")
        print("  (This is okay - the example demonstrates the pattern)")
    
    example_retrieve_metadata()
    example_all_store_implementations()
    example_custom_implementation()
    
    print("\n" + "=" * 70)
    print("✓ All Metadata Store examples completed!")
    print("=" * 70 + "\n")

