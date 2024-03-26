from flask import Flask
from flask_cors import CORS
from config import Config
from app.extensions import db, login_manager, migrate, mail


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from app import auth
    app.register_blueprint(auth.bp)

    from app import claim
    app.register_blueprint(claim.bp)

    from app import user
    app.register_blueprint(user.bp)

    @app.route('/')
    def index():
        return ('Hello, World! - yes the server works, and we can serve static text, or HTML files. Meaning we can '
                'serve packaged-bundled Client-side stuff, whenever client-side team give us a packaged version of '
                'their repository.')

    return app
#
