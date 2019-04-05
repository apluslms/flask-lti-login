
from flask import Flask
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    from ltilogin import views

    app.register_blueprint(views.bp)
    from ltilogin.models import db
    from ltilogin.login import login_manager
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)

    return app
