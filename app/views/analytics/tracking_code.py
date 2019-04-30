from flask import render_template, redirect
from flask_security import current_user, login_required
from app import app, db
from app.models.security import User
from app.models.matomo import *


@app.route('/analytics/tracking_code')
@login_required
def analytics_tracking_code():
    this_user = User.query.filter_by(email=current_user.email).first()

    this_site = Site.query.filter_by(idsite=11).first()
    return render_template('analytics/tracking_code.html', title='Behavee > Analytics > Tracking code', user=this_user, site=this_site)
