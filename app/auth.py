from flask import Blueprint, request, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from flask_cors import cross_origin

from app.models.user import User
from app.extensions import db, login_manager, mail

bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@bp.route('/signup', methods=["POST"])
@cross_origin()
def signup():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user:
        return Response("Username already exists.", 200)

    new_user = User(username=username, password=generate_password_hash(
        password), first_name='', last_name='', active=True, role_id=1,
        email='', profile_picture='default.png')
    db.session.add(new_user)
    db.session.commit()

    return Response("Successfully signed up", 200)


@bp.route('/login', methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return Response("Incorrect login details", 401)

    login_user(user)
    return Response("Successfully logged in", 200)


@bp.route('/request-password-reset', methods=["GET"])
@cross_origin()
@login_required
def request_password_reset():
    return "200"

    msg = Message('Password reset', recipients=[current_user.email])
    msg.body = "Here is your password reset link"
    mail.send(msg)
    return jsonify({'message': 'Password reset link sent to email'}), 200


@bp.route('/change-password', methods=["PUT"])
@cross_origin()
@login_required
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    if not check_password_hash(current_user.password, old_password):
        return jsonify({'error': 'Unauthorised'}), 401

    if check_password_hash(current_user.password, new_password):
        return jsonify({'error': 'New password same as old password'}), 500

    current_user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Successfully changed password'}), 200


@bp.route('/logout', methods=["POST"])
@cross_origin()
def logout():
    logout_user()
    return Response("Successfully logged out", 200)
