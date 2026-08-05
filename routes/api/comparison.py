from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required

from models import (
    db,
    Branch,
    ComparisonHistory
)

from services.serializers import (
    serialize_branch,
    serialize_comparison_history
)
from routes.api.errors import api_error
from routes.api.utils import current_api_user

api_comparison_bp = Blueprint("api_comparison", __name__)


@api_comparison_bp.route("/branches", methods=["GET"])
@jwt_required()
def branches():

    return jsonify({
        "branches": [
            serialize_branch(branch) for branch in Branch.query.all()
        ]
    })


@api_comparison_bp.route("/compare", methods=["POST"])
@jwt_required()
def compare():

    data = request.get_json(silent=True) or {}

    branch1_id = data.get("branch1_id")
    branch2_id = data.get("branch2_id")

    if not branch1_id or not branch2_id:
        return api_error(
            "missing_fields",
            "branch1_id and branch2_id are required.",
            400
        )

    branch1 = Branch.query.get(branch1_id)
    branch2 = Branch.query.get(branch2_id)

    if not branch1 or not branch2:
        return api_error("not_found", "Branch not found.", 404)

    user = current_api_user()

    comparison = ComparisonHistory(
        user_id=user.id,
        branch1_id=branch1.id,
        branch2_id=branch2.id
    )

    db.session.add(comparison)
    db.session.commit()

    return jsonify({
        "comparison_id": comparison.id,
        "branch1": serialize_branch(branch1),
        "branch2": serialize_branch(branch2)
    })


@api_comparison_bp.route("/history", methods=["GET"])
@jwt_required()
def history():

    user = current_api_user()

    comparisons = (
        ComparisonHistory.query
        .filter_by(user_id=user.id)
        .order_by(ComparisonHistory.created_at.desc())
        .all()
    )

    return jsonify({
        "comparisons": [
            serialize_comparison_history(comparison)
            for comparison in comparisons
        ]
    })
