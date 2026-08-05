from services.prediction_service import search_colleges as prediction_search
from tools.tool_registry import TOOLS


def search_colleges(
    exam,
    category,
    quota,
    rank
):
    return prediction_search(
        exam,
        category,
        quota,
        rank
    )


TOOLS["search_colleges"] = {

    "function": search_colleges,

    "description":
        "Predict eligible colleges and branches based on exam, rank, category and quota.",

    "parameters": {

        "exam": "string",

        "category": "string",

        "quota": "string",

        "rank": "integer"
    }

}