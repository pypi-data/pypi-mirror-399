#!/usr/bin/env python3
"""
Example 10: Database Initialization

Demonstrates how to initialize databases for PyCharter metadata stores.
Shows initialization for PostgreSQL, MongoDB, and Redis.
"""

from pycharter import (
    InMemoryMetadataStore,
    MongoDBMetadataStore,
    PostgresMetadataStore,
    RedisMetadataStore,
)

# SQLiteMetadataStore may not be in main __init__ yet, import directly if needed
try:
    from pycharter import SQLiteMetadataStore
except ImportError:
    try:
        from pycharter.metadata_store.sqlite import SQLiteMetadataStore
    except ImportError:
        SQLiteMetadataStore = None


def example_in_memory_initialization():
    """In-memory store requires no initialization."""
    print("=" * 70)
    print("In-Memory Store Initialization")
    print("=" * 70)
    
    print("\n✓ In-memory store requires no initialization")
    print("  Just create and connect:")
    
    store = InMemoryMetadataStore()
    store.connect()
    
    print("  ✓ Connected and ready to use")
    print("  Note: Data is stored in memory and lost when process ends")
    
    store.disconnect()


def example_sqlite_initialization():
    """SQLite initialization - auto-initializes on first use."""
    print("\n" + "=" * 70)
    print("SQLite Initialization (Default)")
    print("=" * 70)
    
    print("\nSQLite is the default database for PyCharter.")
    print("It requires no initialization - tables are created automatically.\n")
    
    if SQLiteMetadataStore is None:
        print("\n  ⚠ SQLiteMetadataStore not available in this installation")
        print("  SQLite support is included by default in PyCharter")
        return
    
    try:
        # Default SQLite database (pycharter.db in current directory)
        connection_string = "sqlite:///pycharter.db"
        
        print(f"Connection string: {connection_string}")
        print("\nStep 1: Create Store (Auto-Initializes)")
        print("-" * 70)
        print("\n  SQLite database is automatically initialized on first use:")
        print("    store = SQLiteMetadataStore(connection_string='sqlite:///pycharter.db')")
        print("    store.connect()  # Creates database and tables if they don't exist")
        
        store = SQLiteMetadataStore(connection_string=connection_string)
        
        print("\n  Connecting...")
        store.connect()
        
        print("  ✓ Connected to SQLite")
        print("  ✓ Database and tables created automatically")
        print("  ✓ Ready to use")
        
        # Test storing a schema
        schema_id = store.store_schema(
            "test_schema",
            {"type": "object", "version": "1.0.0", "properties": {"name": {"type": "string"}}},
            version="1.0.0"
        )
        print(f"\n  ✓ Test schema stored (ID: {schema_id})")
        
        store.disconnect()
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        print("\n  SQLite should work out of the box - no additional setup needed")


def example_postgres_initialization():
    """PostgreSQL initialization using CLI command."""
    print("\n" + "=" * 70)
    print("PostgreSQL Initialization")
    print("=" * 70)
    
    print("\nPostgreSQL requires schema initialization via 'pycharter db init'.")
    print("This follows the same pattern as Airflow's 'airflow db init'.\n")
    
    # Example connection string (adjust for your setup)
    connection_string = "postgresql://postgres:1234567890@localhost:5432/postgres"
    
    print(f"Connection string: {connection_string.replace('1234567890', '***')}")
    print("\nStep 1: Initialize Database Schema (Run Once)")
    print("-" * 70)
    print("\n  Run this command first:")
    print(f"  pycharter db init {connection_string.replace('1234567890', '***')}")
    print("\n  This will:")
    print("    ✓ Create all database tables")
    print("    ✓ Create all indexes")
    print("    ✓ Set up Alembic version tracking")
    
    print("\nStep 2: (Optional) Seed Initial Data")
    print("-" * 70)
    print("\n  Optionally seed the database with initial data (owners, domains, systems):")
    print(f"  pycharter db seed data/seed {connection_string.replace('1234567890', '***')}")
    print("\n  Or use default seed directory:")
    print(f"  pycharter db seed {connection_string.replace('1234567890', '***')}")
    print("\n  This will:")
    print("    ✓ Load sample owners from data/seed/owners.yaml")
    print("    ✓ Load sample domains from data/seed/domains.yaml")
    print("    ✓ Load sample systems from data/seed/systems.yaml")
    print("    ✓ Perform upsert operations (safe to run multiple times)")
    
    print("\nStep 3: Connect and Use")
    print("-" * 70)
    
    try:
        store = PostgresMetadataStore(connection_string=connection_string)
        
        # Connect (only connects and validates, doesn't create tables)
        print("\n  Connecting...")
        store.connect()
        
        print("  ✓ Connected successfully")
        print("  ✓ Schema validated")
        
        # Check schema info
        try:
            schema_info = store.get_schema_info()
            print(f"\n  Schema Info:")
            print(f"    Valid: {schema_info.get('valid', 'N/A')}")
            print(f"    Version: {schema_info.get('version', 'N/A')}")
        except AttributeError:
            print("  (Schema info not available in this version)")
        
        # Test storing a schema
        schema_id = store.store_schema(
            "test_schema",
            {"type": "object", "properties": {"name": {"type": "string"}}},
            version="1.0.0"
        )
        print(f"\n  ✓ Test schema stored (ID: {schema_id})")
        
        store.disconnect()
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        print("\n  Make sure:")
        print("    1. PostgreSQL is running")
        print("    2. Database exists")
        print("    3. Connection string is correct")
        print("    4. Schema is initialized: pycharter db init <connection_string>")
        print("    5. (Optional) Seed data: pycharter db seed data/seed <connection_string>")


def example_mongodb_initialization():
    """MongoDB initialization - no schema needed."""
    print("\n" + "=" * 70)
    print("MongoDB Initialization")
    print("=" * 70)
    
    print("\nMongoDB is schema-less - no initialization needed!")
    print("Collections and indexes are created automatically.\n")
    
    # Example connection string (adjust for your setup)
    connection_string = "mongodb://rootUser:rootPassword@localhost:27017"
    database_name = "pycharter"
    
    print(f"Connection string: {connection_string.replace('rootPassword', '***')}")
    print(f"Database name: {database_name}")
    
    try:
        store = MongoDBMetadataStore(
            connection_string=connection_string,
            database_name=database_name
        )
        
        print("\n  Connecting to MongoDB...")
        store.connect()
        
        print("  ✓ Connected to MongoDB")
        print("  ✓ Collections will be created on first use")
        print("  ✓ Indexes created automatically")
        print("  ✓ Ready to use")
        
        # Test storing a schema
        schema_id = store.store_schema(
            "test_schema",
            {"type": "object", "properties": {"name": {"type": "string"}}},
            version="1.0.0"
        )
        print(f"\n  ✓ Test schema stored (ID: {schema_id})")
        
        # List collections
        if hasattr(store, '_db'):
            collections = store._db.list_collection_names()
            print(f"  Collections: {collections}")
        
        store.disconnect()
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        print("\n  Make sure:")
        print("    1. MongoDB is running")
        print("    2. Connection string is correct")
        print("    3. Authentication credentials are correct")
        print("    4. pymongo is installed: pip install pymongo")


def example_redis_initialization():
    """Redis initialization - no schema needed."""
    print("\n" + "=" * 70)
    print("Redis Initialization")
    print("=" * 70)
    
    print("\nRedis is key-value storage - no schema needed!")
    print("Keys are created automatically when storing data.\n")
    
    # Example connection string (adjust for your setup)
    connection_string = "redis://localhost:6379/0"
    key_prefix = "pycharter"
    
    print(f"Connection string: {connection_string}")
    print(f"Key prefix: {key_prefix}")
    
    try:
        store = RedisMetadataStore(
            connection_string=connection_string,
            key_prefix=key_prefix
        )
        
        print("\n  Connecting to Redis...")
        store.connect()
        
        print("  ✓ Connected to Redis")
        print("  ✓ Keys will be created automatically")
        print("  ✓ Index sets created on first use")
        print("  ✓ Ready to use")
        
        # Test storing a schema
        schema_id = store.store_schema(
            "test_schema",
            {"type": "object", "properties": {"name": {"type": "string"}}},
            version="1.0.0"
        )
        print(f"\n  ✓ Test schema stored (ID: {schema_id})")
        
        # Check keys
        if hasattr(store, '_client'):
            keys = store._client.keys(f"{key_prefix}:*")
            print(f"  Keys created: {len(keys)}")
        
        store.disconnect()
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        print("\n  Make sure:")
        print("    1. Redis is running")
        print("    2. Connection string is correct")
        print("    3. redis package is installed: pip install redis")


def example_connection_strings():
    """Show examples of connection strings for different databases."""
    print("\n" + "=" * 70)
    print("Connection String Examples")
    print("=" * 70)
    
    examples = {
        "PostgreSQL": [
            "postgresql://user:password@localhost:5432/pycharter",
            "postgresql://user:password@localhost/pycharter",
            "postgresql://user@localhost:5432/pycharter",  # No password
            "postgresql://user:password@host.example.com:5432/pycharter",  # Remote
        ],
        "MongoDB": [
            "mongodb://localhost:27017",
            "mongodb://user:password@localhost:27017",
            "mongodb://user:password@localhost:27017/pycharter",
            "mongodb://user:password@host1:27017,host2:27017/pycharter",  # Replica set
        ],
        "Redis": [
            "redis://localhost:6379",
            "redis://localhost:6379/0",  # Database 0
            "redis://:password@localhost:6379",  # With password
            "redis://user:password@localhost:6379/0",
        ],
    }
    
    for db_type, conn_strings in examples.items():
        print(f"\n{db_type}:")
        for conn_str in conn_strings:
            # Mask passwords
            masked = conn_str.replace(":password", ":***").replace(":pass", ":***")
            print(f"  {masked}")


def example_environment_variables():
    """Show how to use environment variables for configuration."""
    print("\n" + "=" * 70)
    print("Using Environment Variables")
    print("=" * 70)
    
    print("""
You can configure database connections using environment variables:

PostgreSQL:
  export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost/pycharter
  export PYCHARTER__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:pass@localhost/pycharter

Then in Python:
  from pycharter import PostgresMetadataStore
  
  # Connection string will be read from environment
  store = PostgresMetadataStore()
  store.connect()

Or pass explicitly:
  import os
  store = PostgresMetadataStore(connection_string=os.getenv("PYCHARTER_DATABASE_URL"))
  store.connect()
    """)


def example_docker_setup():
    """Show Docker setup examples."""
    print("\n" + "=" * 70)
    print("Docker Setup Examples")
    print("=" * 70)
    
    print("""
PostgreSQL (Docker):
  docker run -d \\
    --name pycharter-postgres \\
    -e POSTGRES_USER=postgres \\
    -e POSTGRES_PASSWORD=postgres \\
    -e POSTGRES_DB=pycharter \\
    -p 5432:5432 \\
    postgres:latest
  
  Connection: postgresql://postgres:postgres@localhost:5432/pycharter

MongoDB (Docker):
  docker run -d \\
    --name pycharter-mongo \\
    -e MONGO_INITDB_ROOT_USERNAME=rootUser \\
    -e MONGO_INITDB_ROOT_PASSWORD=rootPassword \\
    -p 27017:27017 \\
    mongodb/mongodb-community-server:latest
  
  Connection: mongodb://rootUser:rootPassword@localhost:27017

Redis (Docker):
  docker run -d \\
    --name pycharter-redis \\
    -p 6379:6379 \\
    redis:latest
  
  Connection: redis://localhost:6379/0
    """)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter - Database Initialization Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    example_in_memory_initialization()
    example_sqlite_initialization()
    example_postgres_initialization()
    example_mongodb_initialization()
    example_redis_initialization()
    example_connection_strings()
    example_environment_variables()
    example_docker_setup()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("""
✓ InMemoryMetadataStore: No initialization needed (testing/development)
✓ SQLiteMetadataStore: Auto-initializes on first use (default, recommended for development)
✓ PostgresMetadataStore: Initialize with 'pycharter db init' (production)
✓ MongoDBMetadataStore: No schema needed, collections created automatically
✓ RedisMetadataStore: No schema needed, keys created automatically

For production PostgreSQL deployments, consider:
  1. Initialize schema separately using CLI: pycharter db init
  2. (Optional) Seed initial data: pycharter db seed data/seed
  3. Connect with validate_schema_on_connect=True (default)
  4. Use environment variables for connection strings

For development, SQLite is the default and requires no setup:
  - Defaults to sqlite:///pycharter.db in current directory
  - Auto-creates database and tables on first use
  - Perfect for local development and testing
    """)
    
    print("=" * 70 + "\n")

