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
    open_cat = Category(name="OPEN")
    ews_cat = Category(name="EWS")
    obc_cat = Category(name="OBC-NCL")
    sc_cat = Category(name="SC")
    st_cat = Category(name="ST")

    db.session.add_all([
        open_cat, 
        ews_cat, 
        obc_cat, 
        sc_cat, 
        st_cat
    ])

    db.session.commit()