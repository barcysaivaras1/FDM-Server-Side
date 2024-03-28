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
    req_password_plaintext = request.json["password"]
    # this assumes the sys-admin sets this password to something sensible
    #  and reasonably secure until the user resets password in their own time

    """
    Ensure that the password is provided
    """
    if not req_password_plaintext or len(req_password_plaintext) <= 0:
        return jsonify({"error": "Password must be provided"}), 400
    #

    """
    Ensure that the current logged-in user is a 'System Admin' (that's the role name)
    """
    query_currentUser_isAdmin = db.session.query(User, Role).filter(
        current_user.id == User.id, 
        current_user.role_id == Role.id, 
        Role.name == "System Admin"
    ).first()
    if query_currentUser_isAdmin is None:
        return jsonify({"error": "Unauthorized"}), 401
    #


    """
    Ensure that the user_id provided exists in the system
    """
    user = User.query.filter_by(id=int(user_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    #


    """
    Reset the password of the user to the provided password.
    This assumes the sys-admin sets this password to something sensible
      and reasonably secure until the user resets password in their own time.
    """
    user.password = generate_password_hash(req_password_plaintext)
    # db.session.add(user)
    # do not add becaue it's already in the ystem
    db.session.commit()
    # Then commit to database!
    return Response("Password reset successfully", 200)
#


# End of File