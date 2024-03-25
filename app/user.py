from flask import Blueprint, jsonify, url_for
from flask_login import login_required, current_user

from app.models.user import User, Role
from app.extensions import login_manager

bp = Blueprint('users', __name__, url_prefix='/users')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@bp.route('/profile', methods=["GET"])
@login_required
def get_profile():
    claims = [{'temp': claim.temp} for claim in current_user.claims]
    profile_picture_file = url_for('static', filename=current_user.profile_picture)

    role = Role.query.filter_by(id=current_user.role_id).first()
    role_name = role.name

    line_manager = User.query.filter_by(id=current_user.manager_id).first()
    line_manager_name = line_manager.name if line_manager else ""

    response_data = dict(username=current_user.username, first_name=current_user.first_name,
                         last_name=current_user.last_name, profile_picture=profile_picture_file,
                         claims=claims, role=role_name, line_manager=line_manager_name)
    return jsonify(response_data), 200


@bp.route('/<user_id>', methods=["GET"])
def get_user(user_id):
    user = User.query.filter_by(id=int(user_id)).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'username': user.username}), 200
