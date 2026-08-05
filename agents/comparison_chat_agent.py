from tools.college_compare import compare_colleges
from agents.chat_helper import answer_with_context


def answer_comparison_question(details):

    result = compare_colleges(
        details["college_1"],
        details["branch_1"],
        details["college_2"],
        details["branch_2"]
    )

    if result is None:
        return (
            "I couldn't find one or both of the branches. "
            "Please check the college and branch names."
        )

    formatted_result = f"""
College 1

College: {result["branch_1"]["college"]}
Branch: {result["branch_1"]["branch"]}

Average Package: {result["branch_1"]["avg_package"]} LPA
Median Package: {result["branch_1"]["median_package"]} LPA
Placement Rate: {result["branch_1"]["placement_rate"]}%
NIRF Rank: {result["branch_1"]["nirf_rank"]}

Fees: ₹{result["branch_1"]["fees"]}

----------------------------------------

College 2

College: {result["branch_2"]["college"]}
Branch: {result["branch_2"]["branch"]}

Average Package: {result["branch_2"]["avg_package"]} LPA
Median Package: {result["branch_2"]["median_package"]} LPA
Placement Rate: {result["branch_2"]["placement_rate"]}%
NIRF Rank: {result["branch_2"]["nirf_rank"]}

Fees: ₹{result["branch_2"]["fees"]}
"""

    context = f"""
Comparison Results

{formatted_result}

Use ONLY the information above.

Format your answer in Markdown.

# Comparison Summary

Briefly summarize the comparison.

# College 1

## Strengths

## Weaknesses

# College 2

## Strengths

## Weaknesses

# Side-by-Side Comparison

Compare:

- Average Package
- Median Package
- Placement Rate
- Fees
- NIRF Rank

# Verdict

Explain which college is better and why.
"""

    return answer_with_context(
        str(details),
        context
    )