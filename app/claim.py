from flask import Blueprint, Response

bp = Blueprint('claims', __name__, url_prefix='/claims')

@bp.route('/', methods=["GET"])
def get_claims():
    return Response(200)