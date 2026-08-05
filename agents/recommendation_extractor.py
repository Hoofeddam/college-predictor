import json

from services.openai_service import chat


SYSTEM_PROMPT = """
You extract recommendation details.

Return ONLY valid JSON.

Format:

{
    "exam": "",
    "category": "",
    "quota": "",
    "rank": null,
    "preferred_branch": "",
    "budget": null
}

Return null for missing values.

Do not explain anything.
"""


def extract_recommendation_details(user_message):

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