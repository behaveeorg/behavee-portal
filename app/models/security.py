#!/usr/bin/env python3
from app import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from datetime import datetime
from flask import request


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __bind_key__ = 'portal'

    id = db.Column(Integer(), primary_key=True)
    user_id = db.Column('user_id', Integer(), ForeignKey('portal_user.id'))
    role_id = db.Column('role_id', Integer(), ForeignKey('portal_role.id'))


# Define Role data-model
class Role(db.Model, RoleMixin):
    __tablename__ = 'portal_role'
    __bind_key__ = 'portal'

    id = db.Column(Integer(), primary_key=True)
    name = db.Column(String(80), unique=True)
    description = db.Column(String(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    __tablename__ = 'portal_user'
    __bind_key__ = 'portal'

    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(255), unique=True)
    password = db.Column(String(255))
    first_name = db.Column(String(255))
    last_name = db.Column(String(255))
    phone = db.Column(String(32))
    last_login_at = db.Column(DateTime())
    current_login_at = db.Column(DateTime())
    last_login_ip = db.Column(String(100))
    current_login_ip = db.Column(String(100))
    login_count = db.Column(Integer)
    active = db.Column(Boolean())
    confirmed_at = db.Column(DateTime())
    roles = relationship('Role', secondary='roles_users', backref=backref('portal_user', lazy='dynamic'))


def register_portal_user(email, first_name, last_name):
    now = datetime.now()
    ip = get_request_ip()
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        last_login_at=now,
        current_login_at=now,
        last_login_ip=ip,
        current_login_ip=ip,
        login_count=1,
        active=1,
        confirmed_at=now
)
    db.session.add(user)
    db.session.commit()


def get_request_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy

# # Define User data-model
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     email = db.Column(db.String(128), unique=True)
#     _password = db.Column(db.String(128))
#     active = db.Column(db.Boolean(), nullable=False, server_default='0')
#
#     first_name = db.Column(db.String(128))
#     last_name = db.Column(db.String(128))
#
#     confirmed_at = db.Column(db.DateTime())
#     last_login_at = db.Column(db.DateTime())
#     current_login_at = db.Column(db.DateTime())
#     last_login_ip = db.Column(db.String(128))
#     current_login_ip = db.Column(db.String(128))
#     login_count = db.Column(db.Integer)
#
#     @property
#     def full_name(self):
#         return '{} {}'.format(self.first_name, self.last_name)
#
#     @hybrid_property
#     def password(self):
#         return self._password
#
#     @password.setter
#     def password(self, plaintext):
#         self._password = bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt(12))
#
#     def check_password(self, plaintext):
#         checkpass = plaintext.encode('utf-8')
#         origpass = self.password
#         return bcrypt.checkpw(checkpass, origpass.encode('utf-8'))
#
#     def get_id(self):
#         return self.login
#
#
# # Define UserEmail data-model
# class UserEmail(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     user = db.relationship('User', uselist=False)
#     email = db.Column(db.String(255), nullable=False, unique=True)
#     created_at = db.Column(db.DateTime())
#     confirmed = db.Column(db.Boolean(), nullable=False, server_default='0')
#     confirmed_at = db.Column(db.DateTime())
#     primary = db.Column(db.Boolean(), nullable=False, server_default='0')
#
#
# # Define UserRole data-model
# class UserRole(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     user = db.relationship('User', uselist=False)
#     role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
#     role = db.relationship('Role', uselist=False)
#
# # Define admin models
# class UserAdmin(sqla.ModelView):
#     page_size = 100
#     # define fields for create page
#     form_create_rules = [
#         rules.Field('first_name'),
#         rules.Field('last_name'),
#         rules.Field('email'),
#         rules.Field('password')
#     ]
#     # define fields for edit page
#     form_edit_rules = [
#         rules.Field('first_name'),
#         rules.Field('last_name'),
#         rules.Field('email'),
#         rules.Field('password')
#     ]
#     column_list = ('first_name','last_name','login')
#     # Automatically display human-readable names for the current and available Roles when creating or editing a User
#     column_auto_select_related = True
#
#     def is_accessible(self):
#         if not current_user.is_active or not current_user.is_authenticated or current_user.is_locked:
#             return False
#         return True
#
#     def _handle_view(self, name, **kwargs):
#         if not self.is_accessible():
#             if current_user.is_authenticated:
#                 # permission denied
#                 abort(403)
#             else:
#                 # login
#                 return redirect(url_for('security.login', next=request.url))
