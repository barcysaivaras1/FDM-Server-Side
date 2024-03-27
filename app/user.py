from flask import Blueprint, jsonify, url_for
from flask_login import login_required, current_user

from app.models.user import User, Role
from app.extensions import login_manager, db

bp = Blueprint('users', __name__, url_prefix='/users')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@bp.route('/', methods=["GET"])
@login_required
def get_all_users():
    role = Role.query.filter_by(id=current_user.role_id).first()

    if role.name != "System Admin":
        return jsonify({'error': 'Unauthorised'}), 401

    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify({'users': users_data}), 200


@bp.route('/profile', methods=["GET"])
@login_required
def get_profile():
    claims = [{'title': claim.title, 'amount': claim.amount} for claim in current_user.claims]
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
@login_required
def get_user(user_id):
    user = User.query.filter_by(id=int(user_id)).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'username': user.username}), 200


@bp.route('/<user_id>/deactivate', methods=["PATCH"])
@login_required
def deactivate_user(user_id):
    user = User.query.filter_by(id=int(user_id)).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    role = Role.query.filter_by(id=current_user.role_id).first()

    if role.name != "System Admin":
        return jsonify({'error': 'Unauthorised'}), 401

    user.active = False
    db.session.commit()
    return jsonify({'message': 'User deactivated'}), 200
