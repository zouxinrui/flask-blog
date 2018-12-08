from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed, identity_loaded,UserNeed
from flask_login import current_user
import logging
from flask import request
from .momentjs import momentjs

# Initial principals
principals = Principal()
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(UserNeed('id'))
# Initial app
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
login = LoginManager(app)
Principal(app)
login.login_view = 'login'
from app import views, models


# Configuration of logger
class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super(RequestFormatter, self).format(record)


formatter = RequestFormatter(
    '%(asctime)s - %(levelname)s - [%(remote_addr)s]: %(message)s'
)

handler = logging.FileHandler('logs/operation.log', encoding='UTF-8')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

logging.basicConfig(filename="logs/system.log",
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                    level=logging.WARN)


# Set time format
app.jinja_env.globals['momentjs'] = momentjs


# Add identity to current user
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.role_name))


