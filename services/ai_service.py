from agents.conversation_manager import process_message

def chat(user_id, message, conversation_id=None):
    return process_message(
        user_id,
        message,
        conversation_id
    )