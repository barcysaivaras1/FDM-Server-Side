import os

from flask import Blueprint, request, jsonify, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.models.user import User, Role
from app.models.claim import ClaimStatus
from app.extensions import login_manager, db

bp = Blueprint('users', __name__, url_prefix='/users')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


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
    claims = []
    for claim in current_user.claims:
        status = ""
        match claim.status:
            case ClaimStatus.PENDING:
                status = "Pending"
            case ClaimStatus.DRAFT:
                status = "Draft"
            case ClaimStatus.APPROVED:
                status = "Approved"
            case ClaimStatus.DENIED:
                status = "Denied"

        claims.append({'title': claim.title, 'description': claim.description, 'amount': claim.amount, 'status': status})

    profile_picture_file = url_for('static', filename='profile-pictures/' + current_user.profile_picture)

    role = Role.query.filter_by(id=current_user.role_id).first()
    role_name = role.name

    line_manager = User.query.filter_by(id=current_user.manager_id).first()
    line_manager_name = line_manager.username if line_manager else ""

    response_data = dict(username=current_user.username, first_name=current_user.first_name,
                         last_name=current_user.last_name, profile_picture=profile_picture_file,
                         claims=claims, role=role_name, line_manager=line_manager_name)
    return jsonify(response_data), 200


@bp.route('/<int:user_id>', methods=["GET"])
@login_required
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'username': user.username}), 200


@bp.route('/<int:user_id>/deactivate', methods=["PATCH"])
@login_required
def deactivate_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    role = Role.query.filter_by(id=current_user.role_id).first()

    if role.name != "System Admin":
        return jsonify({'error': 'Unauthorised'}), 401

    user.active = False
    db.session.commit()
    return jsonify({'message': 'User deactivated'}), 200


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/change-profile-picture', methods=['POST'])
@login_required
def change_profile_picture():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        current_user.profile_picture = filename
        db.session.commit()
        return jsonify({'message': 'Profile picture updated'})
    return "200"


@bp.route('/delete-profile-picture', methods=['POST'])
@login_required
def delete_profile_picture():
    current_user.profile_picture = 'default.png'
    db.session.commit()
    return jsonify({'message': 'Profile picture deleted'})
