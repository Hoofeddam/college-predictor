from rag.loader import load_documents
from rag.cleaner import clean_text
from rag.chunker import chunk_text
from rag.embedder import create_embedding
from rag.qdrant_db import create_collection

documents = load_documents()

print(f"Loaded {len(documents)} documents.")

first_document = documents[0]

cleaned = clean_text(first_document["text"])

chunks = chunk_text(cleaned)

print(f"Created {len(chunks)} chunks.")

embedding = create_embedding(chunks[0])

print(f"Embedding dimension: {len(embedding)}")

create_collection(len(embedding))

from qdrant_client.models import PointStruct
from rag.qdrant_db import store_chunks

points = []

point_id = 0

for document in documents:

    print(f"Processing {document['file_name']}...")

    cleaned = clean_text(document["text"])

    chunks = chunk_text(cleaned)

    for chunk_number, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": document["source"],
                    "file": document["file_name"],
                    "year": document["year"],
                    "page": document["page"],
                    "chunk": chunk_number
                }
            )
        )

        point_id += 1

store_chunks(points)

print(f"\nStored {len(points)} chunks in Qdrant.")