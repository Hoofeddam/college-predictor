from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required

from models import (
    db,
    Exam,
    Category,
    Quota,
    PredictionHistory
)

from services.prediction_service import search_colleges
from services.serializers import (
    serialize_exam,
    serialize_category,
    serialize_quota,
    serialize_prediction_history
)
from routes.api.errors import api_error
from routes.api.utils import current_api_user

api_predictor_bp = Blueprint("api_predictor", __name__)


@api_predictor_bp.route("/options", methods=["GET"])
@jwt_required()
def options():

    return jsonify({
        "exams": [serialize_exam(exam) for exam in Exam.query.all()],
        "categories": [
            serialize_category(category) for category in Category.query.all()
        ],
        "quotas": [serialize_quota(quota) for quota in Quota.query.all()]
    })


@api_predictor_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():

    data = request.get_json(silent=True) or {}

    exam_name = data.get("exam")
    category_name = data.get("category")
    quota_name = data.get("quota")
    rank = data.get("rank")

    if not exam_name or not category_name or not quota_name or rank is None:
        return api_error(
            "missing_fields",
            "exam, category, quota and rank are required.",
            400
        )

    try:
        rank = int(rank)
    except (TypeError, ValueError):
        return api_error("invalid_rank", "rank must be an integer.", 400)

    result = search_colleges(exam_name, category_name, quota_name, rank)

    exam = result["exam"]
    category = result["category"]
    quota = result["quota"]

    if not exam or not category or not quota:
        return api_error(
            "invalid_input",
            "Unknown exam, category or quota.",
            400
        )

    user = current_api_user()

    prediction = PredictionHistory(
        user_id=user.id,
        exam_id=exam.id,
        category_id=category.id,
        quota_id=quota.id,
        rank=rank
    )

    db.session.add(prediction)
    db.session.commit()

    return jsonify({
        "prediction_id": prediction.id,
        "results": result["results"]
    })


@api_predictor_bp.route("/history", methods=["GET"])
@jwt_required()
def history():

    user = current_api_user()

    predictions = (
        PredictionHistory.query
        .filter_by(user_id=user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )

    return jsonify({
        "predictions": [
            serialize_prediction_history(prediction)
            for prediction in predictions
        ]
    })


@api_predictor_bp.route("/history/<int:prediction_id>", methods=["GET"])
@jwt_required()
def history_detail(prediction_id):

    user = current_api_user()

    prediction = PredictionHistory.query.filter_by(
        id=prediction_id,
        user_id=user.id
    ).first()

    if not prediction:
        return api_error("not_found", "Prediction not found.", 404)

    result = search_colleges(
        prediction.exam.name,
        prediction.category.name,
        prediction.quota.name,
        prediction.rank
    )

    return jsonify({
        "prediction": serialize_prediction_history(prediction),
        "results": result["results"]
    })
