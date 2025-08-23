from app.db import db
from sqlalchemy.dialects.postgresql import JSONB


class Philosopher(db.Model):
    __tablename__ = 'playable_philosopher'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    school = db.Column(db.String)
    country = db.Column(db.String)
    birth_date = db.Column(db.Text)
    death_date = db.Column(db.Text)
    info = db.Column(db.Text)
    wiki_image_url = db.Column(db.Text)
    wiki_image_meta = db.Column(JSONB)