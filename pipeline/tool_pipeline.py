from pipeline.context_builder import build_context
from pipeline.formatter import format_response


def run_pipeline(
    tool_name,
    user_message,
    result
):

    context = build_context(
        tool_name,
        result
    )

    return format_response(
        user_message,
        context
    )