from concurrent.futures import ThreadPoolExecutor

from flask import render_template, redirect, request, g, abort
from flask_security import current_user, login_required
from app.models.security import User
from app.models.matomo import *
from app.toolbox.current_site import idsite_required
from app.toolbox.matomo import SitesManager, MatomoError
from app.toolbox.user import get_matomo_user


@app.route('/reports/visits', methods=['GET'])
@login_required
@idsite_required
def reports_visits():
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    site = SitesManager().getSiteFromId(matomo_user.token_auth, request.args.get('idSite'))
    if not site:
        abort(404)

    return render_template('reports/visits.html', title='Behavee > Reports > Visits',
                           user=user, site=site, d=d, app=app, mReportsVisits="active")