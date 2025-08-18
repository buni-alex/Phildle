from flask import Blueprint, jsonify, request, abort
from app.models.philosopher import Philosopher

bp = Blueprint('philosophers', __name__, url_prefix='/api/philosophers')

@bp.route('/all_names')
def get_philosophers_names():
    philosophers = Philosopher.query.order_by(Philosopher.name).all()
    return jsonify([p.name for p in philosophers])

@bp.route('/by_name/<string:name>')
def get_philosopher_by_name(name):
    philosopher = Philosopher.query.filter_by(name=name).first()
    if not philosopher:
        abort(404, description=f"No philosopher found with name '{name}'")

    return jsonify({
        "id": philosopher.id,
        "name": philosopher.name,
        "birth_date": philosopher.birth_date,
        "death_date": philosopher.death_date if philosopher.death_date else None,
        "country": philosopher.country,
        "school": philosopher.school
    })
