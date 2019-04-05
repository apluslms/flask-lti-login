from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from ltilogin import create_app
from ltilogin.models import db

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()