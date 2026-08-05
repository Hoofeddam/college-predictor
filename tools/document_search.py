from services.rag_service import retrieve_context
from tools.tool_registry import TOOLS


def search_documents(
    query,
    limit=5
):
    return retrieve_context(
        query,
        limit
    )


TOOLS["search_documents"] = {

    "function": search_documents,

    "description":
        (
            "Search official counselling documents, "
            "JoSAA, CSAB, JEE and admission brochures."
        ),

    "parameters": {

        "query": "string",

        "limit": "integer"
    }

}