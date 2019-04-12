from flask import Flask, render_template
from flask_login import login_required, current_user, LoginManager
from flask_migrate import Migrate
from ltilogin import lti
from ltilogin.signals import lti_login_authenticated
from example import config
from example.models import db, LTIClient, write_user_to_db


lti_login_authenticated.connect(write_user_to_db)
login_manager = LoginManager()
app = Flask(__name__)
app.config.from_object(config)
login_manager.init_app(app)
db.init_app(app)
with app.app_context():
    db.create_all()
    app.register_blueprint(lti)
    migrate = Migrate(app, db)


# @login_required
@app.route('/', methods=['GET'])
def main_page():
    return render_template('main_page.html', user=current_user)


# @login_required
@app.route('/keys', methods=['GET'])
def keys():
    keys = app.config['LTI_CONFIG']['secret']
    return render_template('keys.html', user=current_user, keys=keys)


if __name__ == '__main__':
    app.run(port=5000, debug=True)