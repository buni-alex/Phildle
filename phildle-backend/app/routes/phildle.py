from flask import Blueprint, jsonify
from datetime import date
from app.models.user import User
from app.models.user_phildle_history import UserPhildleHistory
import jwt
from app.models.daily_phildle import DailyPhildle
import os

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

def get_user_from_jwt():
    from flask import request
    token = request.cookies.get("phildle_jwt")
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return User.query.get(payload["user_uuid"])
    except:
        return None

bp = Blueprint('phildles', __name__, url_prefix='/api')

@bp.route('phildle/by_date/<string:played_on>')
def get_phildle_by_date(date):
    entry = DailyPhildle.query.filter_by(date=date).first()
    if not entry:
        return jsonify({'error': 'No phildle found for that date.'}), 404

    return jsonify({
        'date': entry.date,
        'phildle_id': entry.phildle_id,
        'quote_text': entry.quote_text,
        'philosopher_name': entry.philosopher_name,
        'school': entry.school,
        'country': entry.country,
        'birth_date': entry.birth_date,
        'death_date': entry.death_date if entry.death_date else None
    })

@bp.route('phildle/by_id/<int:phildle_id>')
def get_phildle_by_id(phildle_id):
    entry = DailyPhildle.query.filter_by(phildle_id=phildle_id).first()
    if not entry:
        return jsonify({'error': 'No phildle found for that ID.'}), 404

    return jsonify({
        'date': entry.date,
        'phildle_id': entry.phildle_id,
        'quote_text': entry.quote_text,
        'philosopher_name': entry.philosopher_name,
        'school': entry.school,
        'country': entry.country,
        'birth_date': entry.birth_date,
        'death_date': entry.death_date if entry.death_date else None
    })

@bp.route('/today')
def get_today_phildle():
    today = date.today()
    entry = DailyPhildle.query.filter_by(date=today).first()

    if not entry:
        return jsonify({'error': 'No phildle found for today.'}), 404


    daily_replay = None
    user = get_user_from_jwt()    
    if user:
        play = UserPhildleHistory.query.filter_by(
            user_id=user.id,
            phildle_id=entry.phildle_id
        ).first()
        if play and play.played_on.date() == today:
            daily_replay = {
                'daily_success': play.success,
                'attempts': play.attempts
            }


    return jsonify({
        'date': entry.date,
        'phildle_id': entry.phildle_id,
        'quote_text': entry.quote_text,
        'philosopher_name': entry.philosopher_name,
        'school': entry.school,
        'country': entry.country,
        'birth_date': entry.birth_date,
        'death_date': entry.death_date if entry.death_date else None,
        'daily_replay': daily_replay
    })