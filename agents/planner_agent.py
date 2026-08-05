from services.openai_service import chat
from tools.tool_registry import get_tool_descriptions


def plan(user_message):

    tools = get_tool_descriptions()

    prompt = f"""
You are an AI planner.

Available tools:

{tools}

Choose the SINGLE best tool.

Return ONLY valid JSON.

Example:

{{
    "tool": "compare_colleges",
    "message": "Compare IIT Bombay and IIT Madras CSE"
}}
"""

    messages = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    return chat(messages)