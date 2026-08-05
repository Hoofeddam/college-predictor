from services.openai_service import response


def call_model(messages, tools=None):

    return response(
        messages,
        tools=tools
    )