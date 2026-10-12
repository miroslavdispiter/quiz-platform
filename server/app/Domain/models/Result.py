from app.Database.db import db
from datetime import datetime

class Result(db.Model):
    __tablename__ = "result"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # We store the quiz_id as a string because that's how it is in MongoDB
    quiz_id = db.Column(db.String(50), nullable=False)
    quiz_title = db.Column(db.String(100), nullable=False)

    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)

    time_spent = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # RELATION WITH USER MODEL
    user = db.relationship('User', backref=db.backref('results', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Result {self.user_id} - {self.quiz_title}: {self.percentage}%>"