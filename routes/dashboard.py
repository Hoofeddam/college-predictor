from flask import Blueprint, render_template

from flask_login import (
    login_required,
    current_user
)

from models import (
    PredictionHistory,
    SavedCollege,
    ComparisonHistory
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    predictions = (
        PredictionHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )

    saved_colleges = (
        SavedCollege.query
        .filter_by(user_id=current_user.id)
        .order_by(SavedCollege.created_at.desc())
        .all()
    )

    comparisons = (
        ComparisonHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(ComparisonHistory.created_at.desc())
        .all()
    )

    return render_template(
        "dashboard/dashboard.html",
        user=current_user,
        predictions=predictions,
        saved_colleges=saved_colleges,
        comparisons=comparisons
    )
