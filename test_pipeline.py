from pipeline.tool_pipeline import run_pipeline

result = {
    "college": "IIT Bombay",
    "package": 36.9
}

print(
    run_pipeline(
        "search_colleges",
        "Tell me about IIT Bombay",
        result
    )
)