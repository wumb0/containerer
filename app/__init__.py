#!flask/bin/python
import docker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, utils
from config import FIRST_USER_PASS, FIRST_USER_NAME
from flask_wtf.csrf import CSRFProtect
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_admin.base import MenuLink
from redis import Redis
from rq_scheduler import Scheduler

# initialize the application, import config, setup database, setup CSRF protection
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
CSRFProtect(app)

sched = Scheduler(connection=Redis())

# set up the database model if not already set up
from app import models
db.create_all()
db.session.commit()

# setup the User/Role tables with flask-security, create base users/groups if neccessary
userstore = SQLAlchemyUserDatastore(db, models.User, models.Role)
sec = Security(app, userstore)
try:
    with app.app_context():
        userstore.find_or_create_role(name='admin', description='Administrator')
        userstore.find_or_create_role(name='user', description='General user')
        userstore.create_user(email=FIRST_USER_NAME,
                            password=utils.encrypt_password(FIRST_USER_PASS))
        userstore.add_role_to_user(FIRST_USER_NAME, 'admin')
        db.session.commit()
except: db.session.rollback()

docker_client = docker.from_env()

# get the view controllers for the app
from app.views import main, admin, common

# set up main as a blueprint, add as many blueprints as necessary
app.register_blueprint(main.main)

# configure the admin interface, populate it with pages and links
app_admin = Admin(app, 'Containerer Admin', template_mode='bootstrap3', index_view=admin.AdminIndexView())
app_admin.add_view(admin.ContainerInstanceModelView(models.ContainerInstance, db.session))
app_admin.add_view(admin.UserModelView(models.User, db.session))
app_admin.add_view(admin.RoleModelView(models.Role, db.session))
app_admin.add_link(MenuLink(name='Back to Site', url='/'))
