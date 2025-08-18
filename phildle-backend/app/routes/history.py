from flask import Blueprint, request, jsonify, make_response
import datetime, jwt
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.user_phildle_history import UserPhildleHistory
from app.models.phildle_schedule import PhildleSchedule
from app.models.daily_phildle import DailyPhildle
from app.db import db
import os

bp = Blueprint('history', __name__, url_prefix='/api/history')

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey") # ( , fallback for local dev)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def generate_jwt(user_uuid):
    payload = {
        "user_uuid": str(user_uuid),
        "exp": datetime.now(timezone.utc) + timedelta(days=365)  # UTC-aware
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_user_from_jwt():
    from flask import request
    token = request.cookies.get("phildle_jwt")
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return User.query.get(payload["user_uuid"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        print("JWT decode error:", e)
        return None

@bp.route("/init_user", methods=["GET"])
def init_user():
    user = get_user_from_jwt()

    if not user:
        # new user
        user = User()
        db.session.add(user)
        db.session.commit()
        token = generate_jwt(user.id)
        resp = make_response(jsonify({
            "user_uuid": str(user.id),
            "new_user": True,
            "created_at": user.created_at.isoformat()  # full datetime
        }))
        resp.set_cookie("phildle_jwt", token, httponly=True, samesite='Lax', max_age=365*24*3600)
        return resp

    # existing user
    return jsonify({
        "user_uuid": str(user.id),
        "new_user": False,
        "created_at": user.created_at.isoformat()  # full datetime
    })

@bp.route("/record_play", methods=["POST"])
def record_play():
    user = get_user_from_jwt()
    if not user:
        return jsonify({"error": "No valid user"}), 401

    data = request.json
    phildle_id = data.get("phildle_id")
    attempts = data.get("attempts")
    success = data.get("success")

    if success:
        if attempts is None:
            return jsonify({"error": "Attempts required for successful play"}), 400
    else:
        attempts = None

    # Upsert logic stays
    play = UserPhildleHistory.query.filter_by(user_id=user.id, phildle_id=phildle_id).first()
    if not play:
        play = UserPhildleHistory(
            user_id=user.id,
            phildle_id=phildle_id,
            attempts=attempts,
            success=success
        )
        db.session.add(play)
    else:
        play.success = success
        play.played_on = datetime.now(timezone.utc)

    # Check if this phildle is today's daily
    today = datetime.now(timezone.utc).date()
    daily = DailyPhildle.query.filter_by(date=today).first()

    if daily and phildle_id == daily.phildle_id:
        # Block if already played today's daily
        if play.played_on and play.played_on == today and play.id is not None:
            return jsonify({
                "error": "Already played today's daily",
                "current_streak": user.current_streak,
                "max_streak": user.max_streak
            }), 403

        yesterday = today - timedelta(days=1)

        if success:
            if user.last_daily_success == yesterday:
                user.current_streak += 1
            else:
                user.current_streak = 1
            if user.current_streak > user.max_streak:
                user.max_streak = user.current_streak
            user.last_daily_success = today
        else:
            user.current_streak = 0

        user.last_played = today

    # Commit after all changes
    db.session.commit()
    return jsonify({
        "status": "ok",
        "current_streak": user.current_streak,
        "max_streak": user.max_streak
    })

@bp.route("/user_stats", methods=["GET"], strict_slashes=False)
def getUserStats():
    user = get_user_from_jwt()
    if not user:
        return jsonify({"error": "No valid user"}), 401
    
     # Base query for history
    history = UserPhildleHistory.query.filter_by(user_id=user.id).all()

    # Stats counters
    attempt_counts = {i: 0 for i in range(1, 7)}
    losses = 0

    for h in history:
        if h.success:
            if h.attempts and 1 <= h.attempts <= 5:
                attempt_counts[h.attempts] += 1
        else:
            attempt_counts[6] += 1
            losses += 1

    return jsonify({
        "current_streak": user.current_streak,
        "max_streak": user.max_streak,
        "attempt_distribution": attempt_counts,
        "losses": losses,
        "total_played": len(history)
    })


@bp.route("", methods=["GET"], strict_slashes=False)
def history():
    user = get_user_from_jwt()
    if not user:
        return jsonify({"error": "No valid user"}), 401

    today = datetime.now(timezone.utc).date()

    # Grab phildles joined with their quote text from the view
    phildles = (
        db.session.query(
            PhildleSchedule.id,
            PhildleSchedule.date,
            DailyPhildle.quote_text
        )
        .outerjoin(DailyPhildle, DailyPhildle.phildle_id == PhildleSchedule.id)
        .filter(PhildleSchedule.date <= today)
        .order_by(PhildleSchedule.date.desc())
        .all()
    )

    # User's history as a dict {phildle_id: success_bool}
    user_history = {
        play.phildle_id: play.success
        for play in UserPhildleHistory.query.filter_by(user_id=user.id).all()
    }

    result = []
    for pid, date, quote in phildles:
        if pid in user_history:
            success = user_history[pid]
            status = "success" if success else "fail"
        else:
            status = "not_played"

        result.append({
            "phildle_id": pid,
            "date": date.isoformat(),
            "status": status,
            "quote_preview": " ".join(quote.split()[:5]) + "..." if quote else None
        })

    return jsonify({"phildles": result})