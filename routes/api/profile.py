from flask import Blueprint, jsonify

from flask_jwt_extended import jwt_required

from services.serializers import serialize_user
from routes.api.errors import api_error
from routes.api.utils import current_api_user

api_profile_bp = Blueprint("api_profile", __name__)


@api_profile_bp.route("", methods=["GET"])
@jwt_required()
def profile():

    user = current_api_user()

    if not user:
        return api_error("not_found", "User not found.", 404)

    return jsonify({"user": serialize_user(user)})
