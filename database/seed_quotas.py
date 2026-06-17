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
    ai_quota = Quota(name="AI")
    hs_quota = Quota(name="HS")
    os_quota = Quota(name="OS")

    db.create_all([
        ai_quota, 
        hs_quota, 
        os_quota
    ])

    db.session.commit()