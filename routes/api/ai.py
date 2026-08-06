from flask import Blueprint, request, jsonify, current_app

from flask_jwt_extended import jwt_required

from models import Conversation
from services.ai_service import (
    chat,
    list_conversations,
    get_conversation,
    rename_conversation,
    delete_conversation
)
from services.serializers import serialize_conversation
from routes.api.errors import api_error
from routes.api.utils import current_api_user

api_ai_bp = Blueprint("api_ai", __name__)


@api_ai_bp.route("/chat", methods=["POST"])
@jwt_required()
def ai_chat():

    data = request.get_json(silent=True) or {}

    message = data.get("message")
    conversation_id = data.get("conversation_id")

    if not message:
        return api_error("missing_fields", "message is required.", 400)

    user = current_api_user()

    if conversation_id:

        exists = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user.id
        ).first()

        if not exists:
            return api_error("not_found", "Conversation not found.", 404)

    try:
        result = chat(user.id, message, conversation_id)
    except Exception:
        current_app.logger.exception("AI chat request failed")
        return api_error(
            "chat_failed",
            "Something went wrong while getting a response. Please try again.",
            500
        )

    return jsonify(result)


@api_ai_bp.route("/conversations", methods=["GET"])
@jwt_required()
def conversations():

    user = current_api_user()

    q = request.args.get("q")
    convos = list_conversations(user.id, q=q)

    return jsonify({
        "conversations": [
            serialize_conversation(convo) for convo in convos
        ]
    })


@api_ai_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@jwt_required()
def conversation_detail(conversation_id):

    user = current_api_user()

    conversation = get_conversation(user.id, conversation_id)

    if not conversation:
        return api_error("not_found", "Conversation not found.", 404)

    return jsonify({
        "conversation": serialize_conversation(conversation, include_messages=True)
    })


@api_ai_bp.route("/conversations/<int:conversation_id>", methods=["PATCH"])
@jwt_required()
def rename_conversation_route(conversation_id):

    user = current_api_user()

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if title is None:
        return api_error("missing_fields", "title is required.", 400)

    try:
        conversation = rename_conversation(user.id, conversation_id, title)
    except ValueError as e:
        return api_error("invalid_title", str(e), 400)

    if not conversation:
        return api_error("not_found", "Conversation not found.", 404)

    return jsonify({"conversation": serialize_conversation(conversation)})


@api_ai_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation_route(conversation_id):

    user = current_api_user()

    deleted = delete_conversation(user.id, conversation_id)

    if not deleted:
        return api_error("not_found", "Conversation not found.", 404)

    return "", 204
