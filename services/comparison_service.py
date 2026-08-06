from models import Branch
from services.college_resolution import find_college_candidates
from services.normalizer import normalize_branch


def _college_not_found(query):
    return {
        "status": "not_found",
        "field": "college",
        "query": query,
        "message": f"I couldn't find a college matching \"{query}\"."
    }


def _college_ambiguous(query, result):
    names = [match.college.name for match in result.matches]

    return {
        "status": "ambiguous",
        "field": "college",
        "query": query,
        "candidates": names,
        "message": (
            f"\"{query}\" matches more than one college: "
            f"{', '.join(names)}. Which one did you mean?"
        )
    }


def _branch_not_found(query, college):
    return {
        "status": "not_found",
        "field": "branch",
        "query": query,
        "message": f"I couldn't find a \"{query}\" branch at {college.name}."
    }


def _resolve_college_or_none(college_name):
    """Returns (College, None) on a confident match, or (None, error_dict)."""

    result = find_college_candidates(college_name)

    if result.is_confident:
        return result.best.college, None

    if result.is_ambiguous:
        return None, _college_ambiguous(college_name, result)

    return None, _college_not_found(college_name)


def _branch_data(branch):
    """A complete representation of a compared branch -- useful to any
    consumer (web cards, mobile clients, future APIs/exports), not just the
    handful of fields the current chat card happens to display. Existing
    keys/types are preserved for backward compatibility with anything
    already reading this dict; new keys are additive only.
    """

    college = branch.college

    return {
        "college": college.name,
        "branch": branch.branch_name,
        "avg_package": branch.avg_package,
        "median_package": branch.median_package,
        "placement_rate": branch.placement_rate,
        "fees": college.fees,
        "nirf_rank": college.nirf_rank,
        "college_id": college.id,
        "branch_id": branch.id,
        "branch_code": branch.branch_code,
        "intake": branch.intake,
        "hostel_fees": college.hostel_fees,
        "website": college.website,
        "location": college.location,
        "state": college.state,
        "college_type": college.college_type
    }


def compare_branches(
    college_1,
    branch_1,
    college_2,
    branch_2
):

    branch_1 = normalize_branch(branch_1)
    branch_2 = normalize_branch(branch_2)

    college_one, error = _resolve_college_or_none(college_1)
    if error:
        return error

    college_two, error = _resolve_college_or_none(college_2)
    if error:
        return error

    branch_one = Branch.query.filter(
        Branch.branch_name.ilike(f"%{branch_1}%"),
        Branch.college_id == college_one.id
    ).first()

    branch_two = Branch.query.filter(
        Branch.branch_name.ilike(f"%{branch_2}%"),
        Branch.college_id == college_two.id
    ).first()

    if not branch_one:
        return _branch_not_found(branch_1, college_one)

    if not branch_two:
        return _branch_not_found(branch_2, college_two)

    return {
        "status": "ok",
        "branch_1": _branch_data(branch_one),
        "branch_2": _branch_data(branch_two)
    }
