TOOLS = {}


def get_tool_descriptions():

    descriptions = []

    for name, tool in TOOLS.items():

        print(name)
        print(tool)
        print()
        descriptions.append({
            "name": name,
            "description": tool["description"],
            "parameters": tool["parameters"]
        })

    return descriptions

from tools import college_search
from tools import college_compare
from tools import college_recommend
from tools import document_search