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
    open_seat = SeatType(name="OPEN")
    ews_seat = SeatType(name="EWS")
    obc_seat = SeatType(name="OBC-NCL")
    sc_seat = SeatType(name="SC")
    st_seat = SeatType(name="ST")

    db.create_all([
        open_seat,
        ews_seat,
        obc_seat,
        sc_seat,
        st_seat
    ])

    db.session.commit()