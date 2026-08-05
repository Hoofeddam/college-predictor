from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from services.prediction_service import search_colleges

from models import (
    db,
    Exam,
    Category,
    Quota,
    Cutoff,
    PredictionHistory
)

predictor_bp = Blueprint(
    "predictor",
    __name__
)


@predictor_bp.route("/")
@login_required
def home():

    exams = Exam.query.all()

    categories = Category.query.all()

    quotas = Quota.query.all()

    return render_template(
        "predictor/home.html",
        exams=exams,
        categories=categories,
        quotas=quotas
    )


@predictor_bp.route("/predict")
@login_required
def predict():

    exam_name = request.args.get("exam")
    category_name = request.args.get("category")
    quota_name = request.args.get("quota")
    rank = int(request.args.get("rank"))

    result = search_colleges(
        exam_name,
        category_name,
        quota_name,
        rank
    )

    exam = result["exam"]
    category = result["category"]
    quota = result["quota"]
    results = result["results"]

    if not exam or not category or not quota:
        return render_template(
            "predictor/results.html",
            results=[],
            error="We couldn't recognise that exam, category or quota. Please try again."
        )

    if current_user.is_authenticated:

        prediction = PredictionHistory(
            user_id=current_user.id,
            exam_id=exam.id,
            category_id=category.id,
            quota_id=quota.id,
            rank=rank
        )

        db.session.add(prediction)
        db.session.commit()

    return render_template(
        "predictor/results.html",
        results=results
    )


@predictor_bp.route("/predict-again/<int:prediction_id>")
@login_required
def predict_again(prediction_id):

    prediction = PredictionHistory.query.filter_by(
        id=prediction_id,
        user_id=current_user.id
    ).first_or_404()

    return redirect(
        url_for(
            "predictor.predict",
            exam=prediction.exam.name,
            category=prediction.category.name,
            quota=prediction.quota.name,
            rank=prediction.rank
        )
    )