from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

from app.extensions import db
from app.models.claim import Claim, ClaimStatus

bp = Blueprint('claims', __name__, url_prefix='/claims')


@bp.route('/', methods=["GET", "POST"])
@login_required
def get_claims():
    if request.method == "GET":
        claims = [{'id': claim.id, 'title': claim.title, 'amount': claim.amount} for claim in current_user.claims]
        return jsonify({'claims': claims}), 200
    else:
        title = request.form['title']
        amount = request.form['amount']

        new_claim = Claim(title=title, amount=amount, user_id=current_user.id)
        db.session.add(new_claim)
        db.session.commit()
        return jsonify({'message': 'Claim created successfully'}), 200


@bp.route('/<claim_id>', methods=["GET"])
@login_required
def get_claim(claim_id):
    claim = Claim.query.filter_by(id=int(claim_id)).first()

    if claim.user_id != current_user.get_id():
        return jsonify({'error': 'Unauthorised'}), 401

    return jsonify({'data': {'id': claim.id, 'temp': claim.temp}}), 200


@bp.route('/<claim_id>/review', methods=['PATCH'])
@login_required
def review_claim(claim_id):
    status = request.form['status'].lower()
    claim = Claim.query.filter_by(id=int(claim_id)).first()

    # check if claim belongs to an employee who the user manages
    found = False
    for user in current_user.managed_employees:
        if claim.user_id == user.id:
            found = True
            break

    if not found:
        return jsonify({'error': 'Unauthorised'}), 401

    match status:
        case "pending":
            claim.status = ClaimStatus.PENDING
        case "approved":
            claim.status = ClaimStatus.APPROVED
        case "denied":
            claim.status = ClaimStatus.DENIED
        case _:
            return jsonify({'error': 'Invalid claim status'}), 400

    db.session.commit()
    return jsonify({'message': 'Claim status updated'}), 200


@bp.route('/managed-by', methods=['GET'])
@login_required
def get_review_claims():
    # if user is not a line manager, send error message
    # ...

    claims = []
    for employee in current_user.managed_employees:
        claims += employee.claims

    pending_claims = [{'id': claim.id, 'title': claim.title, 'amount': claim.amount} for claim in claims if claim.status == ClaimStatus.PENDING]

    return jsonify({'claims': pending_claims}), 200
