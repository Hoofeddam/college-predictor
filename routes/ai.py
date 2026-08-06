from flask import Blueprint, render_template, request, session, jsonify, current_app
from flask_login import login_required, current_user
from markdown import markdown
from markupsafe import escape

from models import Conversation
from services.ai_service import (
    chat,
    list_conversations,
    get_conversation,
    rename_conversation,
    delete_conversation
)
from services.serializers import serialize_conversation

ai_bp = Blueprint(
    "ai",
    __name__
)

# Built-in Python-Markdown extensions only — no new dependency. Adds
# tables, fenced ``` code blocks, more forgiving list parsing, and turns
# single newlines into <br> so prose that doesn't use blank-line-separated
# paragraphs still breaks the way it visually looks like it should.
MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "nl2br"]


def _render_message_html(role, content):
    """Shared rendering rule for both the full-page route and the AJAX
    endpoint: assistant text is markdown, user text is escaped plain text
    (never re-interpreted as markdown/HTML).
    """

    if role == "assistant":
        return markdown(content, extensions=MARKDOWN_EXTENSIONS)

    return str(escape(content))


def _serialize_history(conversation):
    return [
        {
            "id": message.id,
            "role": message.role,
            "content_html": _render_message_html(message.role, message.content),
            "created_at": message.created_at.isoformat() if message.created_at else None
        }
        for message in conversation.messages
    ]


@ai_bp.route("/ai", methods=["GET", "POST"])
@login_required
def ai():
    """Legacy full-page-reload flow. Kept as a fallback for when
    JavaScript is unavailable — POST /ai/message is the primary path.
    """

    if request.method == "POST":

        user_message = request.form["message"]

        result = chat(
            current_user.id,
            user_message,
            session.get("conversation_id")
        )

        session["conversation_id"] = result["conversation_id"]

    messages = []

    conversation_id = session.get("conversation_id")

    if conversation_id:

        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()

        if conversation:

            messages = [
                {
                    "role": message.role,
                    "content": _render_message_html(message.role, message.content)
                }
                for message in conversation.messages
            ]

    return render_template(
        "ai/chat.html",
        messages=messages,
        conversation_id=conversation_id
    )


@ai_bp.route("/ai/message", methods=["POST"])
@login_required
def ai_message():
    """Primary chat endpoint. Session-cookie authenticated (same as /ai),
    returns JSON for the AJAX frontend.
    """

    data = request.get_json(silent=True) or {}

    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({
            "error": {
                "code": "missing_message",
                "message": "Please enter a message."
            }
        }), 400

    try:
        result = chat(
            current_user.id,
            user_message,
            session.get("conversation_id")
        )
    except Exception:
        current_app.logger.exception("AI chat request failed")

        return jsonify({
            "error": {
                "code": "chat_failed",
                "message": "Something went wrong while getting a response. Please try again."
            }
        }), 500

    session["conversation_id"] = result["conversation_id"]

    return jsonify({
        "conversation_id": result["conversation_id"],
        "user_message": {
            **result["user_message"],
            "content_html": _render_message_html("user", result["user_message"]["content"])
        },
        "assistant_message": {
            **result["assistant_message"],
            "content_html": _render_message_html("assistant", result["assistant_message"]["content"])
        },
        "meta": result.get("meta", {})
    })


@ai_bp.route("/ai/new", methods=["POST"])
@login_required
def new_chat():
    """Clears the active-conversation pointer from the session. No DB
    write — a conversation row is only created lazily on the first real
    message (existing behavior). This just keeps a page reload consistent
    with a "New Chat" click before that first message is sent.
    """

    session.pop("conversation_id", None)

    return "", 204


@ai_bp.route("/ai/conversations", methods=["GET"])
@login_required
def list_conversations_route():

    q = request.args.get("q")
    conversations = list_conversations(current_user.id, q=q)

    return jsonify({
        "conversations": [serialize_conversation(c) for c in conversations]
    })


@ai_bp.route("/ai/conversations/<int:conversation_id>", methods=["GET"])
@login_required
def get_conversation_route(conversation_id):

    conversation = get_conversation(current_user.id, conversation_id)

    if not conversation:
        return jsonify({
            "error": {"code": "not_found", "message": "Conversation not found."}
        }), 404

    session["conversation_id"] = conversation.id

    return jsonify({
        "conversation": serialize_conversation(conversation),
        "messages": _serialize_history(conversation)
    })


@ai_bp.route("/ai/conversations/<int:conversation_id>", methods=["PATCH"])
@login_required
def rename_conversation_route(conversation_id):

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if title is None:
        return jsonify({
            "error": {"code": "missing_fields", "message": "title is required."}
        }), 400

    try:
        conversation = rename_conversation(current_user.id, conversation_id, title)
    except ValueError as e:
        return jsonify({
            "error": {"code": "invalid_title", "message": str(e)}
        }), 400

    if not conversation:
        return jsonify({
            "error": {"code": "not_found", "message": "Conversation not found."}
        }), 404

    return jsonify({"conversation": serialize_conversation(conversation)})


@ai_bp.route("/ai/conversations/<int:conversation_id>", methods=["DELETE"])
@login_required
def delete_conversation_route(conversation_id):

    deleted = delete_conversation(current_user.id, conversation_id)

    if not deleted:
        return jsonify({
            "error": {"code": "not_found", "message": "Conversation not found."}
        }), 404

    if session.get("conversation_id") == conversation_id:
        session.pop("conversation_id", None)

    return "", 204
