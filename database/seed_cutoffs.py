from app import app
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

with app.app_context():
    jee_adv = Exam.query.filter_by(name="JEE Advanced").first()
    open_cat = Category.query.filter_by(name="OPEN").first()
    ai_quota = Quota.query.filter_by(name="AI").first()
    open_seat = SeatType.query.filter_by(name="OPEN").first()
    round5 = CounsellingRound.query.filter_by(round_no=5).first()

    branches = Branch.query.all()

    closing_ranks = {
        1: 66,
        2: 496,
        3: 1685,

        4: 126,
        5: 625,
        6: 1774,

        7: 171,
        8: 995,
        9: 2369,

        10: 271,
        11: 1293,
        12: 2778,

        13: 466,
        14: 1885,
        15: 3590
    }

    cutoffs = []

    for branch in branches:
        cutoffs.append(
            Cutoff(
                branch_id=branch.id,
                exam_id=jee_adv.id,
                category_id=open_cat.id,
                quota_id=ai_quota.id,
                seat_type_id=open_seat.id,
                round_id=round5.id,
                year=2025,
                opening_rank=None,
                closing_rank=closing_ranks[branch.id]
            )
        )

    db.session.add_all(cutoffs)
    db.session.commit()

    print("Cutoffs inserted!")