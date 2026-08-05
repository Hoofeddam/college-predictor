from flask import Blueprint, jsonify

from flask_jwt_extended import jwt_required

from models import db, College, SavedCollege
from services.serializers import serialize_saved_college
from routes.api.errors import api_error
from routes.api.utils import current_api_user

api_saved_bp = Blueprint("api_saved", __name__)


@api_saved_bp.route("", methods=["GET"])
@jwt_required()
def saved_colleges():

    user = current_api_user()

    colleges = (
        SavedCollege.query
        .filter_by(user_id=user.id)
        .order_by(SavedCollege.created_at.desc())
        .all()
    )

    return jsonify({
        "saved": [serialize_saved_college(saved) for saved in colleges]
    })


@api_saved_bp.route("/<int:college_id>", methods=["POST"])
@jwt_required()
def save_college(college_id):

    if not College.query.get(college_id):
        return api_error("not_found", "College not found.", 404)

    user = current_api_user()

    existing = SavedCollege.query.filter_by(
        user_id=user.id,
        college_id=college_id
    ).first()

    if not existing:
        existing = SavedCollege(user_id=user.id, college_id=college_id)
        db.session.add(existing)
        db.session.commit()

    return jsonify({"saved": serialize_saved_college(existing)}), 201


@api_saved_bp.route("/<int:saved_id>", methods=["DELETE"])
@jwt_required()
def remove_saved(saved_id):

    user = current_api_user()

    saved = SavedCollege.query.filter_by(
        id=saved_id,
        user_id=user.id
    ).first()

    if not saved:
        return api_error("not_found", "Saved college not found.", 404)

    db.session.delete(saved)
    db.session.commit()

    return "", 204
