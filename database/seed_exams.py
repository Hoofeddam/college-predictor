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
    jee_advanced = Exam(name="JEE Advanced")
    jee_main = Exam(name="JEE Main")
    comedk = Exam(name="COMEDK")
    kcet = Exam(name="KCET")
    met = Exam(name="MET")

    db.create_all([
        jee_advanced,
        jee_main,
        comedk,
        kcet,
        met
    ])

    db.session.commit()