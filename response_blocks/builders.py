import logging

logger = logging.getLogger(__name__)

MAX_CARDS_PER_RESPONSE = 5


def build_comparison_blocks(tool_result):

    if not isinstance(tool_result, dict):
        return []

    if tool_result.get("status") != "ok":
        return []

    branch_1 = tool_result.get("branch_1")
    branch_2 = tool_result.get("branch_2")

    if not isinstance(branch_1, dict) or not isinstance(branch_2, dict):
        return []

    return [
        {
            "type": "comparison_card",
            "version": 1,
            "data": {
                "branch_1": branch_1,
                "branch_2": branch_2
            }
        }
    ]


def _college_card_data(college, extra_fields=None):

    data = {
        "college_id": college.get("college_id"),
        "college_name": college.get("college"),
        "branch": college.get("branch"),
        "closing_rank": college.get("closing_rank"),
        "avg_package": college.get("avg_package"),
        "median_package": college.get("median_package"),
        "placement_rate": college.get("placement_rate"),
        "nirf_rank": college.get("nirf_rank"),
        "fees": college.get("fees"),
        "hostel_fees": college.get("hostel_fees"),
        "website": college.get("website")
    }

    if extra_fields:
        data.update(extra_fields)

    return data


def build_recommendation_blocks(tool_result):

    if not isinstance(tool_result, list):
        return []

    blocks = []

    for college in tool_result[:MAX_CARDS_PER_RESPONSE]:

        if not isinstance(college, dict):
            continue

        blocks.append({
            "type": "recommendation_card",
            "version": 1,
            "data": _college_card_data(college)
        })

    return blocks


def build_prediction_blocks(tool_result):

    if not isinstance(tool_result, dict):
        return []

    results = tool_result.get("results")

    if not isinstance(results, list):
        return []

    blocks = []

    for college in results[:MAX_CARDS_PER_RESPONSE]:

        if not isinstance(college, dict):
            continue

        blocks.append({
            "type": "prediction_card",
            "version": 1,
            "data": _college_card_data(college, {
                "exam": college.get("exam"),
                "category": college.get("category"),
                "quota": college.get("quota")
            })
        })

    return blocks


BLOCK_BUILDERS = {
    "compare_colleges": build_comparison_blocks,
    "recommend_colleges": build_recommendation_blocks,
    "search_colleges": build_prediction_blocks
}


def build_blocks_for_tool(tool_name, tool_result):
    """Deterministically maps an already-executed tool's result to a list
    of presentation-ready blocks. Never raises — an unrecognized tool, an
    unexpected result shape, or a builder bug all safely resolve to no
    blocks, leaving the assistant's prose answer as the only content
    (the "fall back to markdown" behavior).
    """

    builder = BLOCK_BUILDERS.get(tool_name)

    if not builder:
        return []

    try:
        blocks = builder(tool_result)
    except Exception:
        logger.exception("Failed to build blocks for tool '%s'", tool_name)
        return []

    return blocks or []
