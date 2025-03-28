import chromadb
from chromadb.config import Settings

def get_chroma_client():
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./data"
    ))
    return client

def init_collections():
    client = get_chroma_client()
    
    # Collection pour les utilisateurs avec cluster
    users_collection = client.get_or_create_collection(
        name="users",
        metadata={"hnsw:space": "cosine", "schema": {
            "cluster": "int",
            "email": "str",
            "preferences": "dict",
        }}
    )
    
    # Collection pour les lieux avec cluster
    places_collection = client.get_or_create_collection(
        name="places",
        metadata={"hnsw:space": "cosine", "schema": {
            "cluster": "int",
            "place_type": "str",
            "rating": "float",
            "types": "list",
        }}
    )
    
    return users_collection, places_collection
