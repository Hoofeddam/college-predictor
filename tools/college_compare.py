from services.comparison_service import compare_branches
from tools.tool_registry import TOOLS


def compare_colleges(
    college_1,
    branch_1,
    college_2,
    branch_2
):
    return compare_branches(
        college_1,
        branch_1,
        college_2,
        branch_2
    )

TOOLS["compare_colleges"] = {

    "function": compare_colleges,

    "description":
        "Compare two engineering colleges or branches.",

    "parameters": {

        "college_1": "string",
        "branch_1": "string",
        "college_2": "string",
        "branch_2": "string"
    }

}