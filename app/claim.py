from datetime import datetime
import os
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.claim import Claim, ClaimStatus, Appeal
from app.models.user import Role
from app.models.receipt import Receipt

import base64
from pathlib import Path

bp = Blueprint('claims', __name__, url_prefix='/claims')

GLOB_FOLDERNAME_RECEIPT_IMAGES = "app/static/receipt-images/"

def get_information_about_claim(claim_instance):
    status = ""
    match claim_instance.status:
        case ClaimStatus.PENDING:
            status = "Pending"
        case ClaimStatus.DRAFT:
            status = "Draft"
        case ClaimStatus.APPROVED:
            status = "Approved"
        case ClaimStatus.DENIED:
            status = "Denied"

    receipts_imageContents = {}

    for receipt in claim_instance.receipts:
        receipt_image_name = receipt.image_uri
        try:
            filename, file_extension = os.path.splitext(receipt_image_name)
            file_extension_withoutDot = file_extension.lstrip(".")
            data_url_scheme_prepend = f"data:image/{file_extension_withoutDot};base64,"
            with open(receipt_image_name, "rb") as image_file:
                imageContentsBase64 = data_url_scheme_prepend + base64.b64encode(image_file.read()).decode("utf-8")
                receipts_imageContents[receipt.image_uri] = imageContentsBase64
            #
        except Exception as e:
            print(e)
        #
    #

    return ({
        "user_id": claim_instance.user_id,
        "claim_id": claim_instance.id, 
        "title": claim_instance.title,
        "amount": claim_instance.amount,
        "currency": claim_instance.currency,
        "expenseType": claim_instance.expensetype,
        "date": claim_instance.date,
        "description": claim_instance.description,
        "status": status,
        "receipts": [
            {
                "id": receipt.id, "title": receipt.title, "image": receipt.image_uri, 
                "imageContentsBase64": receipts_imageContents[receipt.image_uri] if receipt.image_uri in receipts_imageContents else None
            } for receipt in claim_instance.receipts
        ]
    })
#


"""
Image File Saving routine
"""

def save_imageFiles_for_claim(multiple_images, claimInstance: Claim):
    """
    # save_imageFiles_for_claim(multiple_images, claimInstance: Claim)
    : multiple_images: List of FileStorage instances
    : claimInstance: Claim instance

    ### This will automatically commit to the database the new Receipt instances.
    """
    for imageFile in multiple_images:
        original_filename = secure_filename(imageFile.filename)
        receipt_filename = f"claim-{claimInstance.id}_receipt-{len(claimInstance.receipts) + 1}_{original_filename}"

        # check the folder to see if there is a folder named "claim{id}"
        #  if not exists, create it
        #  save the image to the folder

        path_claimIdFolder = Path(GLOB_FOLDERNAME_RECEIPT_IMAGES + f"claim-{claimInstance.id}")
        # check this folder exists
        if not path_claimIdFolder.exists() or not path_claimIdFolder.is_dir():
            path_claimIdFolder.mkdir()
        #

        # save the image to the folder
        # the below division-operator is a macro on Path instance which joins the string to said Path
        #  not actually dividing by a string, that'd be stupid.
        pathToSaveImageFileAt = path_claimIdFolder / receipt_filename
        try:
            print(pathToSaveImageFileAt)
            imageFile.save(pathToSaveImageFileAt)
            str_pathToSaveImageFileAt = str(pathToSaveImageFileAt)
            print(f"Image saved at: {str_pathToSaveImageFileAt}")
        except Exception as e:
            print(e)
            continue
        #

        # return jsonify({
        #     "message": "[DEV TEST: Create Claim] Received FormData, made folder if not there, and print file path.",
        #     "id": None
        # }), 200

        new_receipt = Receipt(
            title=claimInstance.title, 
            image_uri=str_pathToSaveImageFileAt, 
            claim_id=claimInstance.id,
            imageFileName=original_filename
        )
        claimInstance.receipts.append(new_receipt)
        db.session.add(new_receipt)
        db.session.commit()
    #
"""
end Image File Saving routine
"""





@bp.route('/', methods=["GET", "POST"])
@login_required
def get_claims():
    if request.method == "GET":
        claims = [
            get_information_about_claim(claim) for claim in current_user.claims
        ]
        return jsonify({
            "user_id": current_user.id,
            "claims": claims
        }), 200
    else:
        """
        A-Ha Gotcha moment here.
        For route POST /claims/ specifically, this uses FormData (XMLHttpRequest) instead of JSON
        Use `request.form` to access the form data.
        """
        title = request.form['title']
        amount = request.form['amount']
        currency = request.form["currency"]
        expensetype = request.form["type"]
        date = request.form["date"]
        description = request.form["description"]
        multiple_images = request.files.getlist("images[]")

        if len(multiple_images) == 0:
            return jsonify({
                "error": "No images provided."
            }), 400
        #

        print(f"Title: {title}")
        print(f"Amount: {amount}")
        print(f"Currency: {currency}")
        print(f"Type: {expensetype}")
        print(f"Date: {date}")
        print(f"Description: {description}")
        print(f"Number of Images: {len(multiple_images)}")

        

        new_claim = Claim(title=title, description=description, amount=amount, currency=currency,
                          expensetype=expensetype, date=date, status=ClaimStatus.PENDING, user_id=current_user.id)
        db.session.add(new_claim)
        db.session.commit()
        
        save_imageFiles_for_claim(multiple_images, new_claim)
        
        return jsonify({
            "message": "Claim created successfully",
            "id": new_claim.id
        }), 200
    #
#


@bp.route('/<int:claim_id>', methods=["GET"])
@login_required
def get_claim(claim_id):
    # claim_id = int(claim_id)
    claim = Claim.query.filter_by(id=claim_id).first()

    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    #

    if claim.user_id != current_user.get_id():
        return jsonify({'error': 'Unauthorised'}), 401

    return jsonify(get_information_about_claim(claim)), 200



@bp.route("/<int:claim_id>", methods=["PATCH"])
@login_required
def edit_claim(claim_id):
    # claim_id = int(claim_id)
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

    pending_claims = [get_information_about_claim(claim) for claim in claims if claim.status != ClaimStatus.DRAFT]

    return jsonify({'claims': pending_claims}), 200


"""
Section: Draft-Claims
"""
@bp.route("/drafts", methods=["GET"])
@login_required
def get_drafts():
    drafts = [
        get_information_about_claim(claim) for claim in current_user.claims if claim.status == ClaimStatus.DRAFT
    ]
    return jsonify({
        "user_id": current_user.id,
        "drafts": drafts
    }), 200
#

@bp.route("/drafts", methods=["POST"])
@login_required
def make_draft():
    attributes_missing = []
    def get_attribute(attribute_name, alternativeValue=None):
        if request.form.get(attribute_name) is None or request.form.get(attribute_name) == "null":
            attributes_missing.append(attribute_name)
        return request.form.get(attribute_name, alternativeValue)
    #

    title = get_attribute("title")
    if title is None:
        # send back error message
        return jsonify({
            "error": "Title is required to create a draft-claim."
        }), 400
    #

    amount = get_attribute("amount", None)
    currency = get_attribute("currency", None)
    expensetype = get_attribute("type", None)
    current_date = datetime.now()
    date = get_attribute("date", str(current_date))
    if date == "null":
        date = str(current_date)
    #
    description = get_attribute("description", None)
    multiple_images = request.files.getlist("images[]")

    if len(multiple_images) == 0:
        warningMessage = "[Warn] No images were provided."
        attributes_missing.append(warningMessage)
    #

    new_claim = Claim(title=title, description=description, amount=amount, currency=currency,
                      expensetype=expensetype, date=date, status=ClaimStatus.DRAFT, user_id=current_user.id)
    db.session.add(new_claim)
    db.session.commit()

    save_imageFiles_for_claim(multiple_images, new_claim)

    messageText = "Draft-claim created successfully!"
    if len(attributes_missing) > 0:
        messageText += "\n[Warning] You are missing attributes:"
        messageText += "\n\t- " + "\n\t- ".join(attributes_missing)
    #
    return jsonify({
        "message": messageText,
        "id": new_claim.id
    }), 200
#

@bp.route("/drafts/<int:claim_id>", methods=["PATCH"])
@login_required
def edit_draft(claim_id):
    attributes_missing = []
    def get_attribute(attribute_name, alternativeValue=None):
        if request.form.get(attribute_name) is None or request.form.get(attribute_name) == "null":
            attributes_missing.append(attribute_name)
        return request.form.get(attribute_name, alternativeValue)
    #

    claim_id = int(claim_id)
    title = get_attribute("title")
    amount = get_attribute("amount")
    currency = get_attribute("currency")
    expensetype = get_attribute("type")
    date = get_attribute("date")
    description = get_attribute("description")
    multiple_images = request.files.getlist("images[]")


    claim = Claim.query.filter_by(id=claim_id).first()
    if claim is None:
        return jsonify({'error': 'Claim not found'}), 404
    #
    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401
    #

    oldTitle = None
    if title is not None:
        oldTitle = claim.title
        claim.title = title
    #
    claim.description = description
    claim.amount = amount
    claim.currency = currency
    claim.expensetype = expensetype
    current_date = datetime.now()
    if date is None:
        claim.date = str(current_date)
    else:
        claim.date = date
    #

    """
    We delete all receipts/images, because client edits which receipts they have.
    They'd re-submit the images they want to keep.
    """
    # remove all receipts first
    for receipt in claim.receipts:
        db.session.delete(receipt)
    #
    if len(multiple_images) > 0:
        # then save again
        save_imageFiles_for_claim(multiple_images, claim)
    #
    




    # if description is not None:
    #     claim.description = description
    # if amount is not None:
    #     claim.amount = amount
    # if currency is not None:
    #     claim.currency = currency
    # if expensetype is not None:
    #     claim.expensetype = expensetype
    # if date is not None:
    #     claim.date = date
    # #

    db.session.commit()
    altered_title = f"{oldTitle} ➡ {title}" if title is not None else claim.title
    return jsonify({
        "message": f"Claim (id: {claim_id}, title: \"{altered_title}\") updated successfully.",
        "id": claim_id
    }), 200
#

@bp.route("/drafts/<int:claim_id>", methods=["DELETE"])
@login_required
def delete_draft(claim_id):
    print(f"Want to delete a draft, id = {claim_id}")
    claim_id = int(claim_id)
    claim = Claim.query.filter_by(id=claim_id).first()

    if claim is None:
        return jsonify({'error': 'Claim not found'}), 404
    #
    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorised'}), 401
    #
    if claim.status != ClaimStatus.DRAFT:
        return jsonify({'error': 'Claim cannot be deleted'}), 401
    #

    db.session.delete(claim)
    db.session.commit()
    return jsonify({
        "message": "Claim deleted.",
        "id": claim_id
    }), 200
#

@bp.route("/drafts/everything", methods=["DELETE"])
@login_required
def delete_all_drafts():
    drafts = Claim.query.filter_by(user_id=current_user.id, status=ClaimStatus.DRAFT).all()
    for draft in drafts:
        db.session.delete(draft)
    #
    db.session.commit()
    return jsonify({
        "message": "All drafts deleted."
    }), 200
#

# End of File