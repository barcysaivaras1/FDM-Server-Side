from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from flask_cors import cross_origin

from app.extensions import db
from app.models.claim import Claim, ClaimStatus, Appeal
from app.models.user import Role

bp = Blueprint('claims', __name__, url_prefix='/claims')


@bp.route('/', methods=["GET", "POST"])
@login_required
def get_claims():
    if request.method == "GET":
        claims = [{'id': claim.id, 'title': claim.title, 'amount': claim.amount} for claim in current_user.claims]
        return jsonify({'claims': claims}), 200
    else:
        title = request.json['title']
        amount = request.json['amount']
        currency = request.json["currency"]
        expenseType = request.json["type"]
        date = request.json["date"]
        description = request.json["description"]
        imageDataBase64 = request.json["image"]

        new_claim = Claim(title=title, amount=amount, user_id=current_user.id)
        db.session.add(new_claim)
        db.session.commit()
        return jsonify({'message': 'Claim created successfully'}), 200


@bp.route('/<int:claim_id>', methods=["GET"])
@login_required
def get_claim(claim_id):
    claim = Claim.query.filter_by(id=claim_id).first()

    if claim.user_id != current_user.get_id():
        return jsonify({'error': 'Unauthorised'}), 401

    return jsonify({'data': {'id': claim.id, 'temp': claim.temp}}), 200


@bp.route('/<int:claim_id>/review', methods=['PATCH'])
@login_required
def review_claim(claim_id):
    status = request.json['status'].lower()
    claim = Claim.query.filter_by(id=claim_id).first()

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


@bp.route('<int:claim_id>/submit', methods=['POST'])
@login_required
def submit_claim(claim_id):
    claim = Claim.query.filter_by(id=claim_id).first()

    if claim is None:
        return jsonify({'error': 'Claim not found'}), 404

    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401

    if claim.status != ClaimStatus.DRAFT:
        return jsonify({'error': 'Claim already submitted'}), 401

    claim.status = ClaimStatus.PENDING
    db.session.commit()
    return jsonify({'message': 'Claim submitted'}), 200


@bp.route('<int:claim_id>/delete', methods=['POST'])
@login_required
def delete_claim(claim_id):
    claim = Claim.query.filter_by(id=claim_id).first()

    if claim is None:
        return jsonify({'error': 'Claim not found'}), 404

    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401

    if claim.status != ClaimStatus.DRAFT:
        return jsonify({'error': 'Claim cannot be deleted'}), 401

    db.session.delete(claim)
    return jsonify({'message': 'Claim deleted'}), 200


@bp.route('/<int:claim_id>/appeal', methods=['POST', 'GET'])
@login_required
def claim_appeal(claim_id):
    if request.method == 'POST':
        description = request.json['description']
        claim = Claim.query.filter_by(id=claim_id).first()

        if claim.status != ClaimStatus.DENIED:
            return jsonify({'error': 'This claim has not been denied'})

        if claim.appeal is not None:
            return jsonify({'error': 'An appeal already exists for this claim'}), 409

        new_appeal = Appeal(description=description, claim_id=int(claim_id), user_id=current_user.id)
        db.session.add(new_appeal)
        db.session.commit()
        return jsonify({'message': 'Appeal created'}), 201

    else:
        appeal = Appeal.query.filter_by(claim_id=claim_id).first()

        if appeal is None:
            return jsonify({"error": "Appeal not found"}), 404

        return jsonify({"description": appeal.description}), 200


@bp.route('/managed-by', methods=['GET'])
@login_required
def get_review_claims():
    role = Role.query.filter_by(id=current_user.role_id).first()
    if role.name != "Line Manager":
        return jsonify({"error": "Unauthorised"}), 401

    claims = []
    for employee in current_user.managed_employees:
        claims += employee.claims

    pending_claims = [{'id': claim.id, 'title': claim.title, 'amount': claim.amount} for claim in claims if
                      claim.status == ClaimStatus.PENDING]

    return jsonify({'claims': pending_claims}), 200
