from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import (
    db,
    Branch,
    ComparisonHistory
)

comparison_bp = Blueprint(
    "comparison",
    __name__
)


@comparison_bp.route("/compare")
@login_required
def compare():

    branches = Branch.query.all()

    return render_template(
        "comparison/compare.html",
        branches=branches
    )


@comparison_bp.route("/compare-result")
@login_required
def compare_result():

    branch1_id = int(request.args.get("branch1"))
    branch2_id = int(request.args.get("branch2"))

    branch1 = Branch.query.get_or_404(branch1_id)
    branch2 = Branch.query.get_or_404(branch2_id)

    comparison = ComparisonHistory(
        user_id=current_user.id,
        branch1_id=branch1.id,
        branch2_id=branch2.id
    )

    db.session.add(comparison)
    db.session.commit()

    return render_template(
        "comparison/compare_result.html",
        branch1=branch1,
        branch2=branch2
    )