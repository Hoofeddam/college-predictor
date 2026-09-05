from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from datetime import datetime, UTC

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    prediction_history = db.relationship('PredictionHistory', backref='user', lazy=True)
    saved_colleges = db.relationship("SavedCollege", backref="user", lazy=True)
    comparison_history = db.relationship("ComparisonHistory", backref="user", lazy=True)
    
    def __repr__(self):
        return f"<User {self.username}>"


class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    quota_id = db.Column(db.Integer, db.ForeignKey("quota.id"), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    exam = db.relationship("Exam")
    category = db.relationship("Category")
    quota = db.relationship("Quota")

    def __repr__(self):
        return f"<PredictionHistory {self.rank}>"


class SavedCollege(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    college = db.relationship("College")


class ComparisonHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    branch1_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    branch2_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    branch1 = db.relationship("Branch", foreign_keys=[branch1_id])
    branch2 = db.relationship("Branch", foreign_keys=[branch2_id])
    

class College(db.Model): #Information about institutions
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100))
    state = db.Column(db.String(50))
    college_type = db.Column(db.String(50))
    fees = db.Column(db.Integer)
    hostel_fees = db.Column(db.Integer)
    nirf_rank = db.Column(db.Integer)
    website = db.Column(db.String(200))

    branches = db.relationship('Branch', backref='college')

    def __repr__(self):
        return f"<College {self.name}>"
    

class Degree(db.Model):
    # Small, slowly-growing controlled vocabulary (17 distinct values in
    # the real JoSAA dataset at the time this was added: "Bachelor of
    # Technology", "Integrated Master of Science", "Bachelor and Master
    # of Technology (Dual Degree)", etc.) -- normalized into its own
    # table for the same reason Exam/Category/Quota already are, rather
    # than repeating the string on every Branch row.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Degree {self.name}>"


class Branch(db.Model): #Information about courses
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    # Subject-matter label only (e.g. "Electrical Engineering") -- no
    # longer sufficient as identity on its own within a college. Real
    # JoSAA data confirmed cases like IIT Bombay offering "Electrical
    # Engineering" as both a plain 4-year B.Tech and a 5-year B.Tech+
    # M.Tech dual degree: two distinct programs, same label. Identity is
    # now (college_id, branch_name, duration_years, degree_id) -- see
    # uq_branch_identity below. Widened from 100 to 255: the real data
    # contains labels up to 110 characters (dual-degree names with an
    # embedded affiliated-institute note, e.g. "...MBA (IIM Bodh Gaya)").
    branch_name = db.Column(db.String(255), nullable=False)
    branch_code = db.Column(db.String(20))
    intake = db.Column(db.Integer)
    avg_package = db.Column(db.Float) #stored in LPA
    median_package = db.Column(db.Float) #stored in LPA
    placement_rate = db.Column(db.Float) #stored in percentage

    # Structured program metadata, parsed from the source's trailing
    # "(N Years, {degree description})" on each program name.
    duration_years = db.Column(db.Integer, nullable=False)
    degree_id = db.Column(db.Integer, db.ForeignKey('degree.id'), nullable=False)
    # Derived from degree.name at import time (UG / INTEGRATED /
    # DUAL_DEGREE) -- denormalized deliberately, not independent
    # information, kept as a plain column so it's directly filterable/
    # indexable without joining to Degree and pattern-matching its name
    # on every query.
    program_type = db.Column(db.String(20), nullable=False)

    degree = db.relationship('Degree')
    cutoffs = db.relationship('Cutoff', backref='branch')

    __table_args__ = (
        db.UniqueConstraint(
            'college_id', 'branch_name', 'duration_years', 'degree_id',
            name='uq_branch_identity'
        ),
    )

    def __repr__(self):
        return f"<Branch {self.branch_name}>"

    
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    cutoffs = db.relationship('Cutoff', backref='exam')

    def __repr__(self):
        return f"<Exam {self.name}>"
    

class Category(db.Model): #Reservation category
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    cutoffs = db.relationship('Cutoff', backref='category')

    def __repr__(self):
        return f"<Category {self.name}>"


class Quota(db.Model): #Admission quota
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    cutoffs = db.relationship('Cutoff', backref='quota')

    def __repr__(self):
        return f"<Quota {self.name}>"


class SeatType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    cutoffs = db.relationship('Cutoff', backref='seat_type')

    def __repr__(self):
        return f"<SeatType {self.name}>"


class CounsellingRound(db.Model): #Round of counselling
    id = db.Column(db.Integer, primary_key=True)
    round_no = db.Column(db.Integer, unique=True, nullable=False)

    cutoffs = db.relationship('Cutoff', backref='round')

    def __repr__(self):
        return f"<Round {self.round_no}>"
    


class Cutoff(db.Model): #Actual admission eligibility data
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quota_id = db.Column(db.Integer, db.ForeignKey('quota.id'), nullable=False)
    seat_type_id = db.Column(db.Integer, db.ForeignKey('seat_type.id'), nullable=True)
    round_id = db.Column(db.Integer, db.ForeignKey('counselling_round.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    opening_rank = db.Column(db.Integer)
    closing_rank = db.Column(db.Integer, nullable=False)

    # Matches search_colleges()'s exact filter (exam_id, category_id,
    # quota_id, round_id, year equality + closing_rank range) and sort
    # (closing_rank asc) -- see services/prediction_service.py. round_id
    # and year were added when the predictor became dataset-aware (pins to
    # one (year, round) per query instead of mixing every imported year
    # together); the second index supports resolving "latest (year, round)
    # for this exam" without a full table scan.
    __table_args__ = (
        db.Index(
            "ix_cutoff_exam_category_quota_round_year_closing_rank",
            "exam_id", "category_id", "quota_id", "round_id", "year", "closing_rank"
        ),
        db.Index(
            "ix_cutoff_exam_year",
            "exam_id", "year"
        ),
    )

    def __repr__(self):
        return (f"<Cutoff " f"Year:{self.year} " f"Rank:{self.closing_rank}>")


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    title_is_custom = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    messages = db.relationship(
        "Message",
        backref="conversation",
        lazy=True,
        order_by="Message.id",
        cascade="all, delete-orphan"
    )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


# --- Phase 9A: import crosswalk tables -------------------------------
#
# College.id / Branch.id are the canonical identifiers -- these tables
# don't introduce a second identity, they just resolve a given source's
# own name for a college/branch to the existing canonical row, so a
# re-import (or a future second source) reuses rows instead of creating
# duplicates. See scripts/import_data.py.

class CollegeExternalRef(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    external_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    college = db.relationship("College")

    __table_args__ = (
        db.UniqueConstraint(
            "source", "external_name",
            name="uq_college_external_ref_source_name"
        ),
    )

    def __repr__(self):
        return f"<CollegeExternalRef {self.source}:{self.external_name}>"


class BranchExternalRef(db.Model):
    # Scoped to college_id as well as source: raw branch names repeat
    # identically across colleges in the source data (e.g. every college
    # has a "Computer Science and Engineering (4 Years, Bachelor of
    # Technology)" row), so external_name alone isn't a unique key --
    # (college, external_name) is.
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    external_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    branch = db.relationship("Branch")
    college = db.relationship("College")

    __table_args__ = (
        db.UniqueConstraint(
            "source", "college_id", "external_name",
            name="uq_branch_external_ref_source_college_name"
        ),
    )

    def __repr__(self):
        return f"<BranchExternalRef {self.source}:{self.external_name}>"