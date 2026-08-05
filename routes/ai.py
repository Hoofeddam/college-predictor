from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from markdown import markdown

from models import Conversation
from services.ai_service import chat

ai_bp = Blueprint(
    "ai",
    __name__
)


@ai_bp.route("/ai", methods=["GET", "POST"])
@login_required
def ai():

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
                    "content": markdown(message.content)
                }
                for message in conversation.messages
            ]

    return render_template(
        "ai/chat.html",
        messages=messages
    )