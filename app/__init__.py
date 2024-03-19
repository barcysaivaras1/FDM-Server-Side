from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app import auth
    app.register_blueprint(auth.bp)

    from app import claim
    app.register_blueprint(claim.bp)

    return app
