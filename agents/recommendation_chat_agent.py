from tools.college_recommend import recommend_colleges
from agents.chat_helper import answer_with_context


def answer_recommendation_question(details):

    if details["quota"] is None:
        details["quota"] = "AI"

    recommendations = recommend_colleges(
        details["exam"],
        details["category"],
        details["quota"],
        details["rank"],
        details["preferred_branch"],
        details["budget"]
    )

    if not recommendations:
        return (
            "I couldn't find any colleges matching your preferences."
        )

    formatted_results = ""

    for college in recommendations:

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
Recommended Colleges

{formatted_results}

Use ONLY the information above.

Format the answer in Markdown.

# Summary

Briefly explain why these colleges were selected.

# Recommended Colleges

For each college explain:

- Why it is recommended
- Closing Rank
- Average Package
- Median Package
- Placement Rate
- NIRF Rank
- Fees

### Best For

Mention who should choose it.

# Final Recommendation

Recommend the single best option overall.
"""

    return answer_with_context(
        str(details),
        context
    )