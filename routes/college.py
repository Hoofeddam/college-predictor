from flask import Blueprint, render_template

from models import College

college_bp = Blueprint(
    "college",
    __name__
)


@college_bp.route("/college/<int:college_id>")
def college_details(college_id):

    college = College.query.get_or_404(college_id)

    return render_template(
        "college/college_details.html",
        college=college
    )