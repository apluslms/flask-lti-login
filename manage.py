from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from ltilogin import setting
from ltilogin.models import db, create_new_key, create_new_secret ,LTIClient
from ltilogin.login import login_manager
from flask import Flask
from ltilogin import views

app = Flask(__name__)
# app = create_app()
app.register_blueprint(views.bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ltilogin/app.db'
app.config['SECRET_KEY'] = setting.SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
migrate = Migrate()
manager = Manager(app)
manager.add_command('db', MigrateCommand)
db.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)


@manager.command
def add_key(key=create_new_key(), secret=create_new_secret(), description="test"):
    lti = LTIClient(key=key ,secret=secret, description=description)
    db.session.add(lti)
    db.session.commit()

if __name__ == '__main__':
    manager.run()