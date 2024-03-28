from flask import Blueprint, request, Response, jsonify
from flask_login import current_user, login_required
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash


from app.extensions import db, login_manager
from app.models.user import User, Role

bp = Blueprint('admin', __name__, url_prefix='/admin')



@bp.route("/", methods=["GET", "POST"])
@login_required
@cross_origin()
def default_admin_landing_page():
    return jsonify({"message": "Welcome to the admin landing page. There's only '/admin/admin-force-reset-password' right now."}), 200
    pass
#

@bp.route("/admin-force-reset-password/<user_id>", methods=["POST"])
@login_required
@cross_origin
def admin_force_reset_password(user_id):
    ## MUST OVERRIDE/RESET PASSWORD ENTRY OF TABLE ROW representing this User
    req_password_plaintext = request.form.get("password")
    # this assumes the sys-admin sets this password to something sensible
    #  and reasonably secure until the user resets password in their own time
    if not req_password_plaintext or len(req_password_plaintext) <= 0:
        return jsonify({"error": "Password must be provided"}), 400
    #
    user = User.query.filter_by(id=int(user_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    #

    user.password = generate_password_hash(req_password_plaintext)
    # db.session.add(user)
    # do not add becaue it's already in the ystem
    db.session.commit()

    return Response("Password reset successfully", 200)
    pass
#


# End of File