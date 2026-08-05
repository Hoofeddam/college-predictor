from app import app
from agents.conversation_manager import process_message

with app.app_context():

    conversation_id = None

    for message in [
        "Recommend colleges",
        "JEE Advanced",
        "1800",
        "OPEN",
        "AI"
    ]:

        result = process_message(1, message, conversation_id)

        conversation_id = result["conversation_id"]

        print(result["answer"])
