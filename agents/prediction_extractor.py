import json

from services.openai_service import chat

from services.normalizer import (
    normalize_exam,
    normalize_category,
    normalize_quota,
)


SYSTEM_PROMPT = """
You extract structured information from engineering college admission queries.

Return ONLY valid JSON.

Format:

{
    "exam": null,
    "category": null,
    "quota": null,
    "rank": null
}

Definitions:

exam:
- JEE Advanced
- JEE Main
- COMEDK
- KCET
- MET
- etc.

category:
- OPEN
- OBC-NCL
- EWS
- SC
- ST
- etc.

quota:
- AI (All India)
- HS (Home State)
- OS
- etc.

IMPORTANT:

If the user writes:

"JEE Advanced OPEN AI rank 500"

Return:

{
    "exam": "JEE Advanced",
    "category": "OPEN",
    "quota": "AI",
    "rank": 500
}

Another example:

User:
COMEDK GM rank 3000

Return:

{
    "exam": "COMEDK",
    "category": "GM",
    "quota": null,
    "rank": 3000
}

Rules:

- Return ONLY JSON.
- Do not explain anything.
- Missing values must be null.
- Rank must be an integer.
"""

def extract_prediction_details(user_message):

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

    print(response)

    data = json.loads(response)

    data["exam"] = normalize_exam(data["exam"])
    data["category"] = normalize_category(data["category"])
    data["quota"] = normalize_quota(data["quota"])

    print("Normalized:", data)

    return data