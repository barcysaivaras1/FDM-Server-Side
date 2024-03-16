from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import claim
    app.register_blueprint(claim.bp)

    return app