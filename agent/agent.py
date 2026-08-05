from services.openai_service import chat

from agent.prompts import SYSTEM_PROMPT
from agent.parser import parse_response
from agent.executor import execute_action
from tools.tool_registry import get_tool_descriptions


def run_agent(
    user_message,
    conversation=None
):

    tool_descriptions = get_tool_descriptions()

    system_prompt = SYSTEM_PROMPT

    system_prompt += "\n\nAvailable tools:\n\n"

    for tool in tool_descriptions:

        system_prompt += f"Tool: {tool['name']}\n"

        system_prompt += (
            f"Description: {tool['description']}\n"
        )

        system_prompt += "Parameters:\n"

        for parameter, parameter_type in tool["parameters"].items():

            system_prompt += (
                f"- {parameter}: {parameter_type}\n"
            )

        system_prompt += "\n"


    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if conversation:
        messages.extend(conversation)

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    while True:

        response = chat(messages)

        action = parse_response(response)

        print("\n========== Agent ==========")
        print(action)
        print("===========================\n")

        if action["type"] == "ask":
            return action

        if action["type"] == "final":
            return action["answer"]

        tool_result = execute_action(action)

        messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        messages.append(
            {
                "role": "user",
                "content": f"""
        Tool Result:

        {tool_result}

        Using ONLY this tool result, answer the original user question.

        If the tool result contains Source, File, Page or Year information,
        cite them naturally in your answer.

        Example:
        "According to the JoSAA 2026 Information Brochure (Page 41)..."

        Do not invent citations.
        Do not call another tool.
        """
            }
        )