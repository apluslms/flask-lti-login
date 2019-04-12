from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from example import setting
from ltilogin.models import create_new_key, create_new_secret ,LTIClient
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
login_manager.init_app(app)


@manager.command
def add_key(key=create_new_key(), secret=create_new_secret(), description="test"):
    pass


if __name__ == '__main__':
    manager.run()