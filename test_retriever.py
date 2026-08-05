from rag.retriever import search_documents

results = search_documents(
    "What is the Freeze option in JoSAA?"
)

print(f"Found {len(results)} results.\n")

for i, result in enumerate(results, start=1):

    print("=" * 80)
    print(f"Result {i}")
    print("=" * 80)

    print("Score :", result.score)
    print("Source:", result.payload["source"])
    print("File  :", result.payload["file"])

    print("\nText:\n")

    print(result.payload["text"][:1000])

    print("\n")