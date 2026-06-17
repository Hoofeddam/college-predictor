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
    #colleges
    iit_bombay = College(
        name="IIT Bombay",
        location="Mumbai",
        state="Maharashtra",
        college_type="Government",
        fees=1200000,
        hostel_fees=120000,
        nirf_rank=3,
        website="https://www.iitb.ac.in"
    )
    iit_delhi = College(
        name="IIT Delhi",
        location="New Delhi",
        state="Delhi",
        college_type="Government",
        fees=1200000,
        hostel_fees=120000,
        nirf_rank=4,
        website="https://home.iitd.ac.in"
    )
    iit_madras = College(
        name="IIT Madras",
        location="Chennai",
        state="Tamil Nadu",
        college_type="Government",
        fees=1200000,
        hostel_fees=120000,
        nirf_rank=1,
        website="https://www.iitm.ac.in"
    )
    iit_kanpur = College(
        name="IIT Kanpur",
        location="Kanpur",
        state="Uttar Pradesh",
        college_type="Government",
        fees=1200000,
        hostel_fees=120000,
        nirf_rank=5,
        website="https://www.iitk.ac.in"
    )
    iit_kharagpur = College(
        name="IIT Kharagpur",
        location="Kharagpur",
        state="West Bengal",
        college_type="Government",
        fees=1200000,
        hostel_fees=120000,
        nirf_rank=6,
        website="https://www.iitkgp.ac.in"
    )    

    db.session.add_all([
        iit_bombay, 
        iit_delhi, 
        iit_madras, 
        iit_kanpur, 
        iit_kharagpur
        ])

    db.session.commit()