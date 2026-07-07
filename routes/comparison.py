from flask import Blueprint, render_template, request

from models import Branch

comparison_bp = Blueprint(
    "comparison",
    __name__
)


@comparison_bp.route("/compare")
def compare():

    branches = Branch.query.all()

    return render_template(
        "comparison/compare.html",
        branches=branches
    )


@comparison_bp.route("/compare-result")
def compare_result():

    branch1_id = int(request.args.get("branch1"))
    branch2_id = int(request.args.get("branch2"))

    branch1 = Branch.query.get(branch1_id)
    branch2 = Branch.query.get(branch2_id)

    return render_template(
        "comparison/compare_result.html",
        branch1=branch1,
        branch2=branch2
    )