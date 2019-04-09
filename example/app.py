from flask import Flask, render_template
from ltilogin.login import login_manager
from flask_login import login_required
from ltilogin.views import bp, current_user
from ltilogin import setting
from ltilogin.models import db, LTIClient

app = Flask(__name__)
login_manager.init_app(app)
db.init_app(app)
app.register_blueprint(bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = setting.SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@login_required
@app.route('/', methods=['GET'])
def main_page():
    return render_template('main_page.html', user=current_user)

@login_required
@app.route('/keys', methods=['GET'])
def keys():
    keys = LTIClient.query.all()
    return render_template('keys.html', user=current_user, keys=keys)

if __name__ == '__main__':
    app.run(port=5000, debug=True)