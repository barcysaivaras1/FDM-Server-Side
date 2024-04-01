from hmac import new
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from flask_cors import cross_origin

from app.extensions import db
from app.models.claim import Claim, ClaimStatus, Appeal
from app.models.user import Role
from app.models.receipt import Receipt

import base64

bp = Blueprint('claims', __name__, url_prefix='/claims')


def get_information_about_claim(claim_instance):
    return ({
        "user_id": claim_instance.user_id,
        "claim_id": claim_instance.id, 
        "title": claim_instance.title,
        "amount": claim_instance.amount,
        "currency": claim_instance.currency,
        "expenseType": claim_instance.expensetype,
        "date": claim_instance.date,
        "description": claim_instance.description,
        "status": claim_instance.status,
        "receipts": [{"id": receipt.id, "title": receipt.title, "image": receipt.image_uri} for receipt in claim_instance.receipts]
    })
#


@bp.route('/', methods=["GET", "POST"])
@login_required
def get_claims():
    if request.method == "GET":
        print(f"Current user {current_user} wants to get all claims.")
        claims = [
            get_information_about_claim(claim) for claim in current_user.claims
        ]
        return jsonify({
            "user_id": current_user.id,
            "claims": claims
        }), 200
    else:
        print(f"Current user {current_user} wants to create a new claim.")
        title = request.json['title']
        amount = request.json['amount']
        try:
            currency = request.json["currency"]
        except KeyError:
            currency = None
        #
        try:
            expenseType = request.json["type"]
        except KeyError:
            expenseType = None
        #
        try:
            date = request.json["date"]
        except KeyError:
            date = None
        #
        try:
            description = request.json["description"]
        except KeyError:
            description = None
        #
        try:
            imageDataBase64 = request.json["image"]
        except KeyError:
            imageDataBase64 = None
        #

        new_claim = Claim(title=title, amount=amount, user_id=current_user.id)
        db.session.add(new_claim)
        db.session.commit()
        the_claim_id = new_claim.id
        print(f"{current_user} has created: New claim with ID {the_claim_id}.")
        return jsonify({
            'message': 'Claim created successfully',
            "id": the_claim_id
        }), 200
    #
#


@bp.route('/<claim_id>', methods=["GET"])
@login_required
def get_claim(claim_id):
    claim = Claim.query.filter_by(id=claim_id).first()

    if claim.user_id != current_user.get_id():
        return jsonify({'error': 'Unauthorised'}), 401

    return jsonify(get_information_about_claim(claim)), 200



@bp.route("/<int:claim_id>", methods=["PATCH"])
@login_required
def edit_claim(claim_id):
    title = request.json['title']
    amount = request.json['amount']
    currency = request.json["currency"]
    expenseType = request.json["type"]
    date = request.json["date"]
    description = request.json["description"]

    claim = Claim.query.filter_by(id=claim_id).first()

    if claim is None:
        return jsonify({'error': 'Claim not found'}), 404
    #
    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401
    #

    claim.title = title
    claim.description = description
    claim.amount = amount
    claim.currency = currency
    claim.expensetype = expenseType
    claim.date = date

    db.session.commit()
    return jsonify({
        'message': 'Claim updated successfully',
        "id": claim_id
    }), 200
#

@bp.route("/<int:claim_id>/images", methods=["POST"])
@login_required
def add_image_to_claim(claim_id):
    claim = Claim.query.filter_by(id=claim_id).first()
    if claim is None:
        return jsonify({'error': 'Claim not found'}), 404
    #
    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401
    #


    """
    Before going any further, test that the image is in base64 first.
    """
    receiptImageUri_base64encoded = request.json['image']
    print(receiptImageUri_base64encoded)
    receiptImageUri_base64encoded

    receipt_image_name = f"claim-{claim_id}_receipt-{len(claim.receipts) + 1}.png"
    try:
        with open("./static/receipt-images/" + receipt_image_name, "wb") as fh:
            fh.write(base64.decodebytes(receiptImageUri_base64encoded))
        #
    except Exception as e:
        print(e)
    #
    print("Image saved successfully?")

    return jsonify({
        'message': 'TESTING: Image not yet added to claim reciept.',
        "claim_id": claim_id
    }), 200

    """
    End test block.
    """

    receiptTitle = request.json["title"]
    receiptImageUri_base64encoded = request.json['image']
    receiptClaimId = claim_id

    new_receipt = Receipt(title=receiptTitle, image_uri=receiptImageUri_base64encoded, claim_id=receiptClaimId)
    db.session.add(new_receipt)
    db.session.commit()
    return jsonify({
        'message': 'Image added to claim',
        "claim_id": claim_id,
        "receipt_id": new_receipt.id
    }), 200
#

@bp.route("/<int:claim_id>/images", methods=["DELETE"])
@login_required
def remove_image_from_claim(claim_id):
    print("NOT IMPLEMENTED YET: Remove image from claim")
    return jsonify({
        'message': 'TESTING: Image not yet removed from claim reciept.',
        "claim_id": claim_id
    }), 200
#


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
