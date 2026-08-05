from tools.tool_executor import execute_tool


def execute_action(action):

    tool = action["tool"]

    arguments = action["arguments"]

    return execute_tool(
        tool,
        **arguments
    )