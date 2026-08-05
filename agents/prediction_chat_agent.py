from tools.college_search import search_colleges
from agents.chat_helper import answer_with_context


def answer_prediction_question(details):

    if details["quota"] is None:
        details["quota"] = "AI"

    print(details)

    result = search_colleges(
        details["exam"],
        details["category"],
        details["quota"],
        details["rank"]
    )

    if (
        result["exam"] is None
        or result["category"] is None
        or result["quota"] is None
    ):
        return (
            "I couldn't identify the exam, category or quota. "
            "Please provide them clearly."
        )

    formatted_results = ""

    for college in result["results"]:

        formatted_results += f"""
College: {college["college"]}
Branch: {college["branch"]}

Closing Rank: {college["closing_rank"]}
Average Package: {college["avg_package"]} LPA
Median Package: {college["median_package"]} LPA
Placement Rate: {college["placement_rate"]}%
NIRF Rank: {college["nirf_rank"]}

Fees: ₹{college["fees"]}
Hostel Fees: ₹{college["hostel_fees"]}

Website: {college["website"]}

----------------------------------------

"""

    context = f"""
Prediction Results

{formatted_results}
"""

    return answer_with_context(
        str(details),
        context
    )