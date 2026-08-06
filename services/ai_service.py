from models import db, Conversation

from agents.conversation_manager import process_message


def chat(user_id, message, conversation_id=None):
    return process_message(
        user_id,
        message,
        conversation_id
    )


def _escape_like(text):
    """Escapes literal %, _ and the escape character itself, so a search
    term is matched literally rather than as a LIKE/ILIKE wildcard pattern.
    The backslash must be escaped first to avoid double-escaping the
    characters it introduces.
    """

    return (
        text
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def list_conversations(user_id, q=None):
    """Ordered by recent activity. q, if given, filters by title
    (case-insensitive, substring match).
    """

    query = Conversation.query.filter_by(user_id=user_id)

    if q and q.strip():
        term = _escape_like(q.strip())
        query = query.filter(Conversation.title.ilike(f"%{term}%", escape="\\"))

    return query.order_by(Conversation.updated_at.desc()).all()


def get_conversation(user_id, conversation_id):
    return Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()


def rename_conversation(user_id, conversation_id, title):
    """Returns the updated Conversation, or None if not found/not owned.
    Raises ValueError for an empty title.
    """

    conversation = get_conversation(user_id, conversation_id)

    if not conversation:
        return None

    title = (title or "").strip()

    if not title:
        raise ValueError("Title cannot be empty.")

    conversation.title = title[:255]
    conversation.title_is_custom = True

    db.session.commit()

    return conversation


def delete_conversation(user_id, conversation_id):
    """Returns True if deleted, False if not found/not owned."""

    conversation = get_conversation(user_id, conversation_id)

    if not conversation:
        return False

    db.session.delete(conversation)
    db.session.commit()

    return True
