from models import (
    db,
    Exam,
    Category,
    Quota,
    Cutoff
)

from services.normalizer import normalize_exam, normalize_category


def _find_by_name_ci(model, name):

    if not name:
        return None

    return model.query.filter(
        db.func.lower(model.name) == name.strip().lower()
    ).first()


def search_colleges(exam_name, category_name, quota_name, rank):

    exam_name = normalize_exam(exam_name)
    category_name = normalize_category(category_name)

    exam = _find_by_name_ci(Exam, exam_name)
    category = _find_by_name_ci(Category, category_name)
    quota = _find_by_name_ci(Quota, quota_name)

    if not exam or not category or not quota:
        return {
            "exam": None,
            "category": None,
            "quota": None,
            "results": []
        }

    cutoffs = Cutoff.query.filter(
        Cutoff.exam_id == exam.id,
        Cutoff.category_id == category.id,
        Cutoff.quota_id == quota.id,
        Cutoff.closing_rank >= rank
    ).order_by(
        Cutoff.closing_rank.asc()
    ).all()

    results = []

    for cutoff in cutoffs:

        results.append(
            {
                "college_id": cutoff.branch.college.id,
                "college": cutoff.branch.college.name,
                "branch": cutoff.branch.branch_name,
                "exam": exam.name,
                "category": category.name,
                "quota": quota.name,
                "round": cutoff.round.round_no,
                "year": cutoff.year,
                "closing_rank": cutoff.closing_rank,
                "avg_package": cutoff.branch.avg_package,
                "median_package": cutoff.branch.median_package,
                "placement_rate": cutoff.branch.placement_rate,
                "nirf_rank": cutoff.branch.college.nirf_rank,
                "fees": cutoff.branch.college.fees,
                "hostel_fees": cutoff.branch.college.hostel_fees,
                "website": cutoff.branch.college.website
            }
        )

    return {
        "exam": exam,
        "category": category,
        "quota": quota,
        "results": results
    }