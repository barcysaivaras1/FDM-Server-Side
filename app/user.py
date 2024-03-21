from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from app.models.user import User
from app.extensions import login_manager

bp = Blueprint('users', __name__, url_prefix='/users')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@bp.route('/profile', methods=["GET"])
@login_required
def get_profile():
    claims = [{'temp': claim.temp} for claim in current_user.claims]
    response_data = dict(username=current_user.username, first_name=current_user.first_name,
                         last_name=current_user.last_name, claims=claims)
    return jsonify(response_data), 200


@bp.route('/<user_id>', methods=["GET"])
def get_user(user_id):
    user = User.query.filter_by(id=int(user_id)).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'username': user.username}), 200
