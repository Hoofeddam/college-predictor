from rag.retriever import search_documents


def retrieve_context(
    query,
    limit=5
):

    contexts = search_documents(
        query,
        limit
    )

    formatted_context = []

    for context in contexts:

        formatted_context.append(
            f"""
Source: {context["source"]}
File: {context["file"]}
Page: {context["page"]}
Year: {context["year"]}
Similarity: {context["score"]:.3f}

{context["text"]}
"""
        )

    return "\n\n----------------------------------------\n\n".join(
        formatted_context
    )