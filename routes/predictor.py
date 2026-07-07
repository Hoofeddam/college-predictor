from flask import Blueprint, render_template, request

from models import (
    Exam,
    Category,
    Quota,
    Cutoff
)

predictor_bp = Blueprint(
    "predictor",
    __name__
)


@predictor_bp.route("/")
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
def predict():

    exam_name = request.args.get("exam")
    category_name = request.args.get("category")
    quota_name = request.args.get("quota")
    rank = int(request.args.get("rank"))

    exam = Exam.query.filter_by(
        name=exam_name
    ).first()

    category = Category.query.filter_by(
        name=category_name
    ).first()

    quota = Quota.query.filter_by(
        name=quota_name
    ).first()

    if not exam or not category or not quota:
        return "Invalid Input"

    cutoffs = Cutoff.query.filter(
        Cutoff.exam_id == exam.id,
        Cutoff.category_id == category.id,
        Cutoff.quota_id == quota.id,
        Cutoff.closing_rank >= rank
    ).order_by(
        Cutoff.closing_rank.asc()
    ).all()

    return render_template(
        "predictor/results.html",
        cutoffs=cutoffs
    )