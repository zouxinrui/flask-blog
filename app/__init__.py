from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed, identity_loaded,UserNeed
from flask_login import current_user
principals = Principal()  # 实例化一个Principal对象
admin_permission = Permission(RoleNeed('admin')) # 表示满足role有admin的用户才能够有权限
user_permission = Permission(UserNeed('id'))
##################################################################################
import logging
# logging.basicConfig(filename="log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
##################################################################################

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
login = LoginManager(app)
Principal(app)
login.login_view = 'login'
##############################################################################3
handler = logging.FileHandler('flask2.log', encoding='UTF-8')
handler.setLevel(logging.INFO)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)
###############################################################################
from .momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs

from app import views, models


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


