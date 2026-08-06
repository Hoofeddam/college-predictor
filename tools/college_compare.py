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
        "Compare two engineering colleges or branches. Returns a dict with "
        "a \"status\" field: \"ok\" (comparison data is in branch_1/branch_2), "
        "\"not_found\" (a college or branch name in \"query\" did not match "
        "anything — ask the user to confirm the name, do not guess), or "
        "\"ambiguous\" (the name in \"query\" matched more than one college, "
        "listed in \"candidates\" — list them for the user and ask which one "
        "they meant, do not guess).",

    "parameters": {

        "college_1": "string",
        "branch_1": "string",
        "college_2": "string",
        "branch_2": "string"
    }

}