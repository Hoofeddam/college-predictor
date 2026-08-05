import json

from services.openai_service import chat


SYSTEM_PROMPT = """
You extract comparison information.

Return ONLY valid JSON.

Format:

{
    "college_1": "",
    "branch_1": "",
    "college_2": "",
    "branch_2": ""
}

Return null for missing values.

Do not explain anything.
"""


def extract_comparison_details(user_message):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = chat(messages)

    return json.loads(response)