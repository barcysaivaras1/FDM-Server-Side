from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

from app.extensions import db
from app.models.claim import Claim, ClaimStatus, Appeal

bp = Blueprint('appeals', __name__, url_prefix='/appeals')


@bp.route('/', methods=["GET", "POST"])
@login_required
def get_appeals():
    appeals = [{'id': appeal.id, 'description': appeal.description} for appeal in current_user.appeals]
    return jsonify({'appeals': appeals})


@bp.route('/<appeal_id>', methods=["GET"])
@login_required
def get_appeal(appeal_id):
    appeal = Appeal.query.filter_by(id=int(appeal_id)).first()

    if appeal is None:
        return jsonify({'error': 'Appeal not found'})

    if appeal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'})

    return jsonify({'id': appeal.id, 'description': appeal.description}), 200
