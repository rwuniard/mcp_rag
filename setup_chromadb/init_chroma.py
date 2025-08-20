
import chromadb
import sys
import time

print("--- Chroma Initializer ---")

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
RETRIES = 10
DELAY = 5

client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

# Let's first check what methods are available on the client
print("\n--- Available Client Methods ---")
available_methods = [method for method in dir(client) if not method.startswith('_')]
print("Available methods:", available_methods)

# 1. Wait for ChromaDB to be available
print("Attempting to connect to ChromaDB...")
for i in range(RETRIES):
    try:
        client.heartbeat()
        print("Successfully connected to ChromaDB.")
        break
    except Exception as e:
        print(f"Connection attempt {i+1}/{RETRIES} failed: {e}")
        if i < RETRIES - 1:
            print(f"Retrying in {DELAY} seconds...")
            time.sleep(DELAY)
        else:
            print("Could not connect to ChromaDB after several retries. Exiting.")
            sys.exit(1)

# 2. Check if multi-tenancy is supported
print("\n--- Checking Multi-tenancy Support ---")
has_tenant_support = hasattr(client, 'get_tenant') and hasattr(client, 'create_tenant')
has_database_support = hasattr(client, 'get_database') and hasattr(client, 'create_database')

print(f"Tenant support: {has_tenant_support}")
print(f"Database support: {has_database_support}")

if has_tenant_support and has_database_support:
    print("Multi-tenancy is supported. Setting up default tenant and database...")
    
    # Ensure the default tenant exists
    try:
        client.get_tenant("default_tenant")
        print("Tenant 'default_tenant' already exists.")
    except Exception as e:
        print("Tenant 'default_tenant' not found, creating it...")
        try:
            client.create_tenant("default_tenant")
            print("Tenant 'default_tenant' created.")
        except Exception as create_error:
            print(f"Failed to create tenant: {create_error}")
            sys.exit(1)

    # Ensure the default database exists
    try:
        client.get_database("default_database", tenant="default_tenant")
        print("Database 'default_database' already exists.")
    except Exception as e:
        print("Database 'default_database' not found, creating it...")
        try:
            client.create_database("default_database", tenant="default_tenant")
            print("Database 'default_database' created.")
        except Exception as create_error:
            print(f"Failed to create database: {create_error}")
            sys.exit(1)
else:
    print("Multi-tenancy is NOT supported in this version of ChromaDB.")
    print("This is normal for older versions. ChromaDB will work directly with collections.")

# 3. Test basic functionality by creating a test collection
print("\n--- Testing Basic Collection Operations ---")
try:
    # Try to get or create a test collection
    test_collection = client.get_or_create_collection("initialization_test")
    print(f"Successfully created/accessed collection: {test_collection.name}")
    
    # List all collections to confirm it exists
    collections = client.list_collections()
    print(f"Total collections in ChromaDB: {len(collections)}")
    for collection in collections:
        print(f"  - {collection.name}")
        
except Exception as e:
    print(f"Error testing basic collection operations: {e}")
    sys.exit(1)

print("\nChromaDB initialization complete.")
