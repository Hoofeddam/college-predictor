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
    

class Branch(db.Model): #Information about courses
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    branch_name = db.Column(db.String(100), nullable=False)
    branch_code = db.Column(db.String(20))
    intake = db.Column(db.Integer)
    avg_package = db.Column(db.Float) #stored in LPA
    median_package = db.Column(db.Float) #stored in LPA
    placement_rate = db.Column(db.Float) #stored in percentage

    cutoffs = db.relationship('Cutoff', backref='branch')

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

    def __repr__(self):
        return (f"<Cutoff " f"Year:{self.year} " f"Rank:{self.closing_rank}>")


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    messages = db.relationship(
        "Message",
        backref="conversation",
        lazy=True,
        order_by="Message.id"
    )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))