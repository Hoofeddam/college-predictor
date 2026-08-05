from models import Branch
from services.normalizer import normalize_branch


def compare_branches(
    college_1,
    branch_1,
    college_2,
    branch_2
):

    branch_1 = normalize_branch(branch_1)
    branch_2 = normalize_branch(branch_2)

    branch_one = Branch.query.filter(
        Branch.branch_name.ilike(f"%{branch_1}%"),
        Branch.college.has(name=college_1)
    ).first()

    branch_two = Branch.query.filter(
        Branch.branch_name.ilike(f"%{branch_2}%"),
        Branch.college.has(name=college_2)
    ).first()

    if not branch_one or not branch_two:
        return None


    return {
        "branch_1": {
            "college": branch_one.college.name,
            "branch": branch_one.branch_name,
            "avg_package": branch_one.avg_package,
            "median_package": branch_one.median_package,
            "placement_rate": branch_one.placement_rate,
            "fees": branch_one.college.fees,
            "nirf_rank": branch_one.college.nirf_rank
        },
        "branch_2": {
            "college": branch_two.college.name,
            "branch": branch_two.branch_name,
            "avg_package": branch_two.avg_package,
            "median_package": branch_two.median_package,
            "placement_rate": branch_two.placement_rate,
            "fees": branch_two.college.fees,
            "nirf_rank": branch_two.college.nirf_rank
        }
    }