from services.openai_service import chat


def answer_with_context(user_message, context):

    prompt = f"""
    You are an experienced Indian engineering admission counselor.

    The following information comes from the application's PostgreSQL database.

    {context}

    IMPORTANT RULES

    - Use ONLY the information above.
    - Never invent facts.
    - If information is missing, clearly say so.
    - Do not repeat the same statistic multiple times.
    - Keep the answer concise and easy to read.
    - Format the answer using Markdown.

    Use this structure whenever applicable:

    # Summary

    Briefly explain what the results mean.

    # Colleges

    For every college:

    ## College Name — Branch

    Why this is a good option.

    - Closing Rank:
    - Average Package:
    - Median Package:
    - Placement Rate:
    - NIRF Rank:

    ### Trade-offs

    Mention any drawbacks.

    # Recommendation

    Recommend the single best option and explain why.
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

    print(messages)

    return chat(messages)