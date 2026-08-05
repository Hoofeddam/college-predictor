from tools.tool_registry import TOOLS
from agent.prompts import SYSTEM_PROMPT


def build_system_prompt():

    prompt = SYSTEM_PROMPT

    prompt += "\n\nAvailable Tools:\n\n"

    for tool in TOOLS.values():

        schema = tool["schema"]

        prompt += f"Tool: {schema['name']}\n"
        prompt += f"Description: {schema['description']}\n\n"

        prompt += "Parameters:\n"

        properties = schema["parameters"]["properties"]
        required = schema["parameters"]["required"]

        for name, info in properties.items():

            prompt += (
                f"- {name} "
                f"({info['type']})"
            )

            if name in required:
                prompt += " [required]"

            prompt += (
                f": {info['description']}\n"
            )

        prompt += "\n"