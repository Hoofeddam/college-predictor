import time

from datetime import datetime, UTC

from models import db, Conversation, Message

from agent.agent import run_agent
from services.serializers import serialize_message

TITLE_MAX_LENGTH = 60


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


def _derive_title(message_text):
    """Temporary, regenerable fallback title from the first user message.
    Never treated as final — title_is_custom stays False so a future
    smarter title-generation feature can safely overwrite it. Only a
    user-initiated rename sets title_is_custom to True, which locks it.
    """

    text = " ".join(message_text.split())

    if len(text) <= TITLE_MAX_LENGTH:
        return text

    return text[:TITLE_MAX_LENGTH].rstrip() + "…"


def process_message(
    user_id,
    user_message,
    conversation_id=None
):

    conversation = _get_or_create_conversation(user_id, conversation_id)

    if conversation.title is None:
        conversation.title = _derive_title(user_message)
        conversation.title_is_custom = False

    history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in conversation.messages
    ]

    started_at = time.monotonic()

    response = run_agent(
        user_message,
        history
    )

    elapsed_ms = int((time.monotonic() - started_at) * 1000)

    if response["type"] == "ask":
        answer = response["question"]
        blocks = []
    else:
        answer = response["text"]
        blocks = response.get("blocks", [])

    user_message_row = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_message
    )

    assistant_message_row = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    db.session.add(user_message_row)
    db.session.add(assistant_message_row)

    conversation.updated_at = datetime.now(UTC)

    db.session.commit()

    assistant_message = serialize_message(assistant_message_row)
    assistant_message["blocks"] = blocks

    return {
        "conversation_id": conversation.id,
        "answer": answer,
        "user_message": serialize_message(user_message_row),
        "assistant_message": assistant_message,
        "meta": {
            "elapsed_ms": elapsed_ms
        }
    }
