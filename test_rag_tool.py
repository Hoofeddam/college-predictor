from rag.retriever import search_documents

results = search_documents(
    "What is the Freeze option in JoSAA?"
)

for i, result in enumerate(results):

    print("=" * 60)
    print("Result", i + 1)
    print("Score:", result.score)
    print(result.payload)