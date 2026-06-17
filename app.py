from flask import Flask, render_template, request

from config import Config

from models import (
    db,
    College,
    Branch,
    Exam,
    Category,
    Quota,
    SeatType,
    CounsellingRound,
    Cutoff
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():

    exams = Exam.query.all()

    categories = Category.query.all()

    quotas = Quota.query.all()

    return render_template(
        "home.html",
        exams=exams,
        categories=categories,
        quotas=quotas
    )


@app.route("/college/<int:college_id>")
def college_details(college_id):

    college = College.query.get_or_404(college_id)

    return render_template(
        "college_details.html",
        college=college
    )


@app.route("/predict")
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
        "results.html",
        cutoffs=cutoffs
    )


@app.route("/compare")
def compare():

    branches = Branch.query.all()

    return render_template(
        "compare.html",
        branches=branches
    )


@app.route("/compare-result")
def compare_result():

    branch1_id = int(request.args.get("branch1"))
    branch2_id = int(request.args.get("branch2"))

    branch1 = Branch.query.get(branch1_id)
    branch2 = Branch.query.get(branch2_id)

    return render_template(
        "compare_result.html",
        branch1=branch1,
        branch2=branch2
    )

if __name__ == "__main__":
    app.run(debug=True)