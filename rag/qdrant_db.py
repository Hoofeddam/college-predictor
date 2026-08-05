from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import VectorParams
from qdrant_client.models import PointStruct

client = QdrantClient(path="qdrant_db")

COLLECTION_NAME = "college_documents"


def create_collection(vector_size):

    collections = client.get_collections().collections

    existing = [
        c.name
        for c in collections
    ]

    if COLLECTION_NAME in existing:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

def store_chunks(chunks):

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=chunks
    )