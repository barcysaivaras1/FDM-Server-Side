from flask import Blueprint, Response

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=["POST"])
def signup():
    return Response(200)

@bp.route('/login', methods=["POST"])
def login():
    return Response(200)

@bp.route('/logout', methods=["POST"])
def logout():
    return Response(200)