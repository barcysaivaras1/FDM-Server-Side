from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.models.claim import Appeal

bp = Blueprint('appeals', __name__, url_prefix='/appeals')


@bp.route('/', methods=["GET"])
@login_required
def get_appeals():
    appeals = [{'id': appeal.id, 'description': appeal.description} for appeal in current_user.appeals]
    return jsonify({'appeals': appeals}), 200


@bp.route('/<int:appeal_id>', methods=["GET"])
@login_required
def get_appeal(appeal_id):
    appeal = Appeal.query.filter_by(id=appeal_id).first()

    if appeal is None:
        return jsonify({'error': 'Appeal not found'}), 404

    if appeal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401

    return jsonify({'id': appeal.id, 'description': appeal.description}), 200
