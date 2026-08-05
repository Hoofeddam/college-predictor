from rag.loader import load_documents
from rag.cleaner import clean_text
from rag.chunker import chunk_text

documents = load_documents()

print(f"Loaded {len(documents)} documents.\n")

for document in documents:

    cleaned = clean_text(document["text"])

    chunks = chunk_text(cleaned)

    print("=" * 80)
    print(f"Document : {document['file_name']}")
    print(f"Chunks   : {len(chunks)}")
    print("=" * 80)

    # Print the first 3 chunks
    for i, chunk in enumerate(chunks[:3], start=1):
        print(f"\n----- Chunk {i} -----\n")
        print(chunk[:600])   # Show only first 600 characters
        print()

    print("\n")