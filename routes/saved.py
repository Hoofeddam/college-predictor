from flask import Blueprint, redirect, render_template

from flask_login import login_required, current_user

from models import (
    db,
    SavedCollege
)

saved_bp = Blueprint(
    "saved",
    __name__
)


@saved_bp.route("/save/<int:college_id>")
@login_required
def save_college(college_id):

    existing = SavedCollege.query.filter_by(
        user_id=current_user.id,
        college_id=college_id
    ).first()

    if not existing:

        saved = SavedCollege(
            user_id=current_user.id,
            college_id=college_id
        )

        db.session.add(saved)
        db.session.commit()

    return redirect("/dashboard")


@saved_bp.route("/saved")
@login_required
def saved_colleges():

    colleges = (
        SavedCollege.query
        .filter_by(user_id=current_user.id)
        .order_by(SavedCollege.created_at.desc())
        .all()
    )

    return render_template(
        "saved/saved_colleges.html",
        colleges=colleges
    )


@saved_bp.route("/remove-saved/<int:saved_id>")
@login_required
def remove_saved(saved_id):

    saved = SavedCollege.query.filter_by(
        id=saved_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(saved)
    db.session.commit()

    return redirect("/saved")