from services.openai_service import chat
from agents.registry import AGENTS
import json


def detect_intent(user_message):

    message = user_message.lower()

    if any(word in message for word in [
        "compare",
        "vs",
        "better"
    ]):
        return "comparison"

    if any(word in message for word in [
        "recommend",
        "suggest"
    ]):
        return "recommendation"

    if any(word in message for word in [
        "predict",
        "cutoff",
        "eligible",
        "rank"
    ]):
        return "prediction"

    return "knowledge"


def execute(intent, data):

    if intent == "knowledge":
        from agents.knowledge_agent import answer_question
        return answer_question(data)

    return AGENTS[intent]["handler"](data)

def plan(user_message):

    agent_descriptions = ""

    for name, agent in AGENTS.items():

        agent_descriptions += f"""
{name}

{agent["description"]}

"""

    prompt = f"""
You are an AI router for an engineering college counselling assistant.

Your job is to choose the SINGLE best agent.

Available agents:

{agent_descriptions}

Guidelines:

- If the user asks which colleges they can get using a rank,
  choose prediction.

- If the user wants suggestions based on preferences,
  budget, branch or location,
  choose recommendation.

- If the user compares colleges or branches,
  choose comparison.

- Otherwise choose knowledge.

Return ONLY valid JSON.

Include a short reason explaining why you selected that agent.

Example:

{{
    "agent": "prediction"
    "reason": "The user is asking for colleges based on rank."
}}
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

    response = chat(messages)

    return json.loads(response)