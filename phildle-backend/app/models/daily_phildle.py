from app.db import db

class DailyPhildle(db.Model):
    __tablename__ = 'daily_phildle'
    __table_args__ = {'extend_existing': True}

    date = db.Column(db.Date, primary_key=True)
    phildle_id = db.Column(db.Integer)
    quote_text = db.Column(db.Text, nullable=False)
    philosopher_name = db.Column(db.Text)
    school = db.Column(db.Text)
    country = db.Column(db.Text)
    birth_date = db.Column(db.Text)
    death_date = db.Column(db.Text)

