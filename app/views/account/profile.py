from flask import render_template, redirect, url_for
from flask_security import current_user, login_required
from app import app,db
from app.models.security import User
from app.models.matomo import *
from app.toolbox.matomo import UsersManager
from time import strftime


@app.route('/account/profile')
@login_required
def account_profile():
    d = {}
    c_user_email = None
    user = None
    matomo_user = None
    if current_user.is_authenticated:
        c_user_email = current_user.email
        user = User.query.filter_by(email=c_user_email).first()
        if user is None:
            return redirect(url_for('users_login'))

        d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
        d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

        # ToDo change to API
        matomo_user = MatomoUser.query.filter_by(email=current_user.email).first()
        if matomo_user is None:
            m = UsersManager()
            r = m.addUser(current_user.email, app.config['MATOMO_ADMIN_TOKEN'])
            matomo_user = MatomoUser.query.filter_by(email=current_user.email).first()

    return render_template('account/profile.html', title='Behavee > Account > Profile', user=user, d=d, matomo_user=matomo_user, menuSettingsProfile="active")
