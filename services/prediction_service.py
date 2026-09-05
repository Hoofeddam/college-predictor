from models import (
    db,
    Exam,
    Category,
    Quota,
    CounsellingRound,
    Cutoff
)

from services.normalizer import normalize_exam, normalize_category


def _find_by_name_ci(model, name):

    if not name:
        return None

    return model.query.filter(
        db.func.lower(model.name) == name.strip().lower()
    ).first()


def get_latest_dataset(exam_id):
    """Returns the (year, round_no) of the most recently imported official
    counselling dataset for this exam, or None if this exam has no cutoff
    data at all. Scoped per exam rather than computed globally, so JEE
    Advanced and JEE Main (or a future exam) each resolve to their own
    latest year/round even if one is imported ahead of the other.

    Deliberately computed from the data itself (highest year, then highest
    round_no within that year) instead of an "is_current" flag maintained
    by whoever runs an import -- nothing to remember to update, and a new
    yearly/round import becomes "the default" the moment it's committed.
    """
    return (
        db.session.query(Cutoff.year, CounsellingRound.round_no)
        .join(CounsellingRound, Cutoff.round_id == CounsellingRound.id)
        .filter(Cutoff.exam_id == exam_id)
        .order_by(Cutoff.year.desc(), CounsellingRound.round_no.desc())
        .first()
    )


def search_colleges(exam_name, category_name, quota_name, rank, year=None, round_no=None):
    """year/round_no are optional. When omitted (every current caller),
    the search resolves to the latest available dataset for the given exam
    -- see get_latest_dataset(). Passing them explicitly targets a specific
    past dataset instead, for future historical/comparison features;
    nothing about past years is deleted or hidden by the default behavior.
    """

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
            "year": None,
            "round": None,
            "results": []
        }

    if year is None or round_no is None:
        latest = get_latest_dataset(exam.id)
        if latest is None:
            return {
                "exam": exam,
                "category": category,
                "quota": quota,
                "year": None,
                "round": None,
                "results": []
            }
        if year is None:
            year = latest[0]
        if round_no is None:
            round_no = latest[1]

    round_row = CounsellingRound.query.filter_by(round_no=round_no).first()
    if round_row is None:
        return {
            "exam": exam,
            "category": category,
            "quota": quota,
            "year": year,
            "round": round_no,
            "results": []
        }

    cutoffs = Cutoff.query.filter(
        Cutoff.exam_id == exam.id,
        Cutoff.category_id == category.id,
        Cutoff.quota_id == quota.id,
        Cutoff.round_id == round_row.id,
        Cutoff.year == year,
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
        "year": year,
        "round": round_no,
        "results": results
    }