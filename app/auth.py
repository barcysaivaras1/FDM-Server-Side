from flask import Blueprint, request, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required

from app.models.user import User, Role
from app.extensions import db, login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@bp.route('/test', methods=["GET"])
@login_required
def test():
    role = Role.query.filter_by(id=current_user.role_id).first()
    print(current_user.claims)
    return Response(f"User ID: {current_user.get_id()}, Username: {current_user.username}, Role: {role.name}", 200)

@bp.route('/signup', methods=["POST"])
def signup():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user:
        return Response("Username already exists.", 200)

    new_user = User(username=username, password=generate_password_hash(password), first_name='', last_name='', active=True, role_id=1) 
    db.session.add(new_user)
    db.session.commit()

    return Response("Successfully signed up", 200)

@bp.route('/login', methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return Response("Incorrect login details", 401)

    login_user(user)
    return Response("Successfully logged in", 200)

@bp.route('/logout', methods=["POST"])
def logout():
    logout_user()
    return Response("Successfully logged out", 200)