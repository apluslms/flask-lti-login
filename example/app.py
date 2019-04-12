from flask import Flask, render_template
from flask_login import login_required, current_user, LoginManager
from flask_migrate import Migrate

from example import config
from example.models import db, User, write_user_to_db
from flask_lti_login import lti, lti_login_authenticated

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


@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user


@login_required
@app.route('/', methods=['GET'])
def main_page():
    return render_template('main_page.html', user=current_user)


@login_required
@app.route('/keys', methods=['GET'])
def keys():
    lti_keys = app.config['LTI_CONFIG']
    return render_template('keys.html', user=current_user, keys=lti_keys)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
