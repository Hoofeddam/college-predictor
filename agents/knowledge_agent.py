from services.openai_service import chat
from rag.retriever import search_documents

SYSTEM_PROMPT = """
You are an expert AI college counselor for Indian engineering admissions.

Answer the user's question ONLY using the provided context.

If the answer is not present in the context,
say you do not know.

Do not invent information.

If multiple context chunks are provided,
combine them into one helpful answer.
"""

def answer_question(user_message):

    results = search_documents(user_message)

    context = ""

    for result in results:

        context += (
            f"Source: {result.payload['source']}\n"
            f"File: {result.payload['file']}\n\n"
            f"{result.payload['text']}\n\n"
            "-------------------------\n\n"
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"Context:\n\n{context}"
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    return chat(messages)