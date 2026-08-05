from services.recommendation_service import recommend
from tools.tool_registry import TOOLS


def recommend_colleges(
    exam,
    category,
    quota,
    rank,
    preferred_branch=None,
    budget=None
):
    return recommend(
        exam,
        category,
        quota,
        rank,
        preferred_branch,
        budget
    )


TOOLS["recommend_colleges"] = {

    "function": recommend_colleges,

    "description":
        "Recommend colleges based on preferences like preferred branch, budget, location or placements. Do NOT use this tool for rank prediction.",

    "parameters": {

        "exam": "string",
        "category": "string",
        "quota": "string",
        "rank": "integer",
        "preferred_branch": "string",
        "budget": "integer"
    }

}