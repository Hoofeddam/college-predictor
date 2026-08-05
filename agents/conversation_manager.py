from models import db, Conversation, Message

from agent.agent import run_agent


def _get_or_create_conversation(user_id, conversation_id):

    conversation = None

    if conversation_id:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        db.session.add(conversation)
        db.session.flush()

    return conversation


def process_message(
    user_id,
    user_message,
    conversation_id=None
):

    conversation = _get_or_create_conversation(user_id, conversation_id)

    history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in conversation.messages
    ]

    response = run_agent(
        user_message,
        history
    )

    if isinstance(response, str):
        answer = response
    else:
        answer = response["question"]

    db.session.add(Message(
        conversation_id=conversation.id,
        role="user",
        content=user_message
    ))

    db.session.add(Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    ))

    db.session.commit()

    return {
        "conversation_id": conversation.id,
        "answer": answer
    }
