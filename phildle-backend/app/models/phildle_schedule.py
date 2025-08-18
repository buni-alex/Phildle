from app.db import db

class PhildleSchedule(db.Model):
    __tablename__ = 'phildle_schedule'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    philosopher_id = db.Column(db.Integer)
    quote_id = db.Column(db.Integer)
    date = db.Column(db.Date)

    #daily = db.relationship("DailyPhildle", back_populates="schedule", uselist=False)