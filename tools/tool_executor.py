from tools.tool_registry import TOOLS


def execute_tool(name, **kwargs):

    tool = TOOLS.get(name)

    if tool is None:
        return None

    return tool["function"](**kwargs)