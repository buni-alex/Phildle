#CREATE TABLE phildle_user (
#    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#    last_played DATE,          -- optional, for streak calculation
#    current_streak INT DEFAULT 0,
#    max_streak INT DEFAULT 0
#);

from app.db import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    __tablename__ = 'phildle_user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_played = db.Column(db.Date)
    last_daily_success = db.Column(db.Date)
    current_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)

    # Optional: relationship to user_phildle_history
    #plays = db.relationship("UserPhildleHistory", back_populates="user")