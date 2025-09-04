import chromadb
import subprocess

chroma_client = chromadb.HttpClient(host="http://localhost:8000")
print("Connected to ChromaDB server")

server_heartbeat = chroma_client.heartbeat()
print(f"Server heartbeat: {server_heartbeat}")

# Get API version
try:
    api_version = chroma_client.get_version()
    print(f"ChromaDB API Version: {api_version}")
except AttributeError:
    print("get_version() method not available")

# Get Docker image version
try:
    docker_image = subprocess.check_output([
        "docker", "inspect", "chromadb", "--format={{.Config.Image}}"
    ], text=True).strip()
    print(f"Docker Image: {docker_image}")
except subprocess.CalledProcessError:
    print("Could not get Docker image version")

# Get actual server version from container
try:
    server_version = subprocess.check_output([
        "docker", "exec", "chromadb", "chroma", "--version"
    ], text=True).strip()
    print(f"Server Version: {server_version}")
except subprocess.CalledProcessError:
    print("Could not get server version from container")
    
# List available collections
try:
    collections = chroma_client.list_collections()
    print(f"Collections: {[col.name for col in collections]}")
except Exception as e:
    print(f"Error listing collections: {e}")
