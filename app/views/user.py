from flask import (Blueprint, render_template, redirect, url_for, abort, flash)
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from app import app, db
from app.models.security import User
from app.forms import user as user_forms
from app.toolbox import email
from datetime import datetime

# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Create a user blueprint
userbp = Blueprint('userbp', __name__, url_prefix='/user')

@userbp.route('/logout')
def signout():
    logout_user()
    flash('Succesfully logged out.', 'positive')
    return redirect(url_for('index'))

@userbp.route('/change')
@login_required
def change_password():
    return redirect(app.config['SECURITY_CHANGE_URL'])