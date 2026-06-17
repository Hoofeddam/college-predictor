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
    iit_bombay = College.query.filter_by(name="IIT Bombay").first()
    iit_delhi = College.query.filter_by(name="IIT Delhi").first()
    iit_madras = College.query.filter_by(name="IIT Madras").first()
    iit_kanpur = College.query.filter_by(name="IIT Kanpur").first()
    iit_kharagpur = College.query.filter_by(name="IIT Kharagpur").first()

    cse_bombay = Branch(
        college_id=iit_bombay.id,
        branch_name="Computer Science and Engineering",
        branch_code="CSE",
        intake=199,
        avg_package=36.9,
        median_package=30.0,
        placement_rate=96.0
    )

    ee_bombay = Branch(
        college_id=iit_bombay.id,
        branch_name="Electrical Engineering",
        branch_code="EE",
        intake=113,
        avg_package=28.5,
        median_package=24.0,
        placement_rate=92.0
    )

    me_bombay = Branch(
        college_id=iit_bombay.id,
        branch_name="Mechanical Engineering",
        branch_code="ME",
        intake=211,
        avg_package=19.0,
        median_package=16.0,
        placement_rate=83.0
    )

    cse_delhi = Branch(
        college_id=iit_delhi.id,
        branch_name="Computer Science and Engineering",
        branch_code="CSE",
        intake=99,
        avg_package=35.0,
        median_package=29.0,
        placement_rate=97.0
    )

    ee_delhi = Branch(
        college_id=iit_delhi.id,
        branch_name="Electrical Engineering",
        branch_code="EE",
        intake=110,
        avg_package=30.0,
        median_package=25.0,
        placement_rate=93.0
    )

    me_delhi = Branch(
        college_id=iit_delhi.id,
        branch_name="Mechanical Engineering",
        branch_code="ME",
        intake=85,
        avg_package=22.8,
        median_package=18.0,
        placement_rate=85.0
    )

    cse_madras = Branch(
        college_id=iit_madras.id,
        branch_name="Computer Science and Engineering",
        branch_code="CSE",
        intake=87,
        avg_package=32.0,
        median_package=26.0,
        placement_rate=95.0
    )

    ee_madras = Branch(
        college_id=iit_madras.id,
        branch_name="Electrical Engineering",
        branch_code="EE",
        intake=148,
        avg_package=24.0,
        median_package=20.0,
        placement_rate=90.0
    )

    me_madras = Branch(
        college_id=iit_madras.id,
        branch_name="Mechanical Engineering",
        branch_code="ME",
        intake=169,
        avg_package=16.0,
        median_package=13.0,
        placement_rate=80.0
    )

    cse_kanpur = Branch(
        college_id=iit_kanpur.id,
        branch_name="Computer Science and Engineering",
        branch_code="CSE",
        intake=121,
        avg_package=34.0,
        median_package=27.0,
        placement_rate=96.0
    )

    ee_kanpur = Branch(
        college_id=iit_kanpur.id,
        branch_name="Electrical Engineering",
        branch_code="EE",
        intake=164,
        avg_package=26.0,
        median_package=21.0,
        placement_rate=91.0
    )

    me_kanpur = Branch(
        college_id=iit_kanpur.id,
        branch_name="Mechanical Engineering",
        branch_code="ME",
        intake=173,
        avg_package=18.0,
        median_package=15.0,
        placement_rate=82.0
    )

    cse_kharagpur = Branch(
        college_id=iit_kharagpur.id,
        branch_name="Computer Science and Engineering",
        branch_code="CSE",
        intake=188,
        avg_package=31.0,
        median_package=25.0,
        placement_rate=94.0
    )

    ee_kharagpur = Branch(
        college_id=iit_kharagpur.id,
        branch_name="Electrical Engineering",
        branch_code="EE",
        intake=170,
        avg_package=22.0,
        median_package=18.0,
        placement_rate=88.0
    )

    me_kharagpur = Branch(
        college_id=iit_kharagpur.id,
        branch_name="Mechanical Engineering",
        branch_code="ME",
        intake=180,
        avg_package=15.0,
        median_package=12.0,
        placement_rate=78.0
    )

    db.session.add_all([
        cse_bombay,
        ee_bombay,
        me_bombay,

        cse_delhi,
        ee_delhi,
        me_delhi,

        cse_madras,
        ee_madras,
        me_madras,

        cse_kanpur,
        ee_kanpur,
        me_kanpur,

        cse_kharagpur,
        ee_kharagpur,
        me_kharagpur
    ])

    db.session.commit()