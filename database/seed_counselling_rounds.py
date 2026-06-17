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
    r1 = CounsellingRound(round_no=1)
    r2 = CounsellingRound(round_no=2)
    r3 = CounsellingRound(round_no=3)
    r4 = CounsellingRound(round_no=4)
    r5 = CounsellingRound(round_no=5)

    db.create_all([
        r1, 
        r2, 
        r3, 
        r4, 
        r5
    ])

    db.session.commit()