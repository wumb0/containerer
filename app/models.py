from app import db, app
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security import UserMixin, RoleMixin, current_user

""" a third table must be created to relate users to roles by id.
    this is an example of a many-to-many relationship in SQLAlchemy
    i.e. a user can have many roles and roles can have many users
"""
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


"""
User: defines users and their attribles for the website
Parents: db.Model, flask.ext.security.UserMixin
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    """flask admin needs this to print the user correctly"""
    def __str__(self):
        return self.email

    """
    hybrid_property is cool. this is a lame example, but you can do complex
    operations in the function and it can be called as an attribute
    to tell if a user is an admin I would do user.is_admin instead of
    user.is_admin() like a normal function
    """
    @hybrid_property
    def is_admin(self):
        return self.has_role('admin')


"""
Role: the table for roles on the site
Parents: db.Model, flask.ext.security.RoleMixin
"""
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    """flask admin needs this to print the role correctly"""
    def __str__(self):
        return self.name


class ContainerInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64))
    pubkey = db.Column(db.String(252))
    privkey = db.Column(db.String(384))
    port = db.Column(db.Integer)

    @hybrid_property
    def username(self):
        return app.config["USERNAME_PREFIX"] + "_" + str(self.id)
