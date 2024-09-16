import os
import chromadb

# Get the storage path from the environment variable, with a default fallback
storage_path = os.getenv("CHROMADB_STORAGE_PATH", "/Users/yifeiwan/Projects/GPT4DFCI-API/chromadb")

# Initialize the ChromaDB Persistent Client
chroma_client = chromadb.PersistentClient(path=storage_path)
