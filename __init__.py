
from flask import Flask


def create_app():
    app = Flask(__name__)

    from . import lti

    app.register_blueprint(lti.bp)
    from .models import db
    from .login import login_manager
    db.init_app(app)
    login_manager.init_app(app)

    return app
