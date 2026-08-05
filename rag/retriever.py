from rag.embedder import create_embedding
from rag.qdrant_db import client, COLLECTION_NAME


def search_documents(query, limit=5):

    query_embedding = create_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    )

    contexts = []

    for point in results.points:

        contexts.append(
            {
                "text": point.payload["text"],
                "source": point.payload["source"],
                "file": point.payload["file"],
                "year": point.payload["year"],
                "page": point.payload["page"],
                "chunk": point.payload["chunk"],
                "score": point.score
            }
        )

    return contexts