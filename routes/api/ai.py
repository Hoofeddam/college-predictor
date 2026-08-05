from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required

from models import Conversation
from services.ai_service import chat
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

    result = chat(user.id, message, conversation_id)

    return jsonify(result)


@api_ai_bp.route("/conversations", methods=["GET"])
@jwt_required()
def conversations():

    user = current_api_user()

    convos = (
        Conversation.query
        .filter_by(user_id=user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    return jsonify({
        "conversations": [
            serialize_conversation(convo) for convo in convos
        ]
    })


@api_ai_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@jwt_required()
def conversation_detail(conversation_id):

    user = current_api_user()

    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=user.id
    ).first()

    if not conversation:
        return api_error("not_found", "Conversation not found.", 404)

    return jsonify({
        "conversation": serialize_conversation(conversation, include_messages=True)
    })
