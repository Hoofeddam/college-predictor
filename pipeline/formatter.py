from services.openai_service import chat


def format_response(user_message, context):

    prompt = f"""
You are an AI Engineering College Counselor.

Use ONLY the information below.

{context}

Answer the user's question in Markdown.

Question:
{user_message}
"""

    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]

    return chat(messages)