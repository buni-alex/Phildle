from app.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class UserPhildleHistory(db.Model):
    __tablename__ = 'user_phildle_history'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('phildle_user.id'), nullable=False)
    phildle_id = db.Column(db.Integer, db.ForeignKey('phildle_schedule.id'), nullable=False)
    attempts = db.Column(db.Integer, nullable=True)
    success = db.Column(db.Boolean, nullable=False)
    played_on = db.Column(db.DateTime, default=datetime.now())

    #user = db.relationship("User", back_populates="plays")