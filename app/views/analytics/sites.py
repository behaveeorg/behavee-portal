from concurrent.futures import ThreadPoolExecutor
from functools import partial

from flask import render_template, redirect, request, g, abort, url_for
from flask_security import current_user, login_required
from app import app, db, session, flask
from app.models.packages import PackageManager
from app.models.security import User
from app.models.matomo import *
from app.toolbox.matomo import SitesManager, MatomoError
from app.forms.analytics.sites import WebsiteForm, SiteDeleteForm
from app.toolbox.user import get_matomo_user, partner_required
from app.toolbox.current_site import idsite_required
from datetime import datetime

SITE_SESSION_KEY = 'matomo_site_id'


@app.route('/analytics/sites', methods=['GET'])
@login_required
def analytics_sites():
    d = {}
    site = None
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    idsite = request.args.get('idSite')
    if idsite:
        site = SitesManager().getSiteFromId(matomo_user.token_auth, idsite)
    else:
        site_list = SitesManager().getMatomoSites(matomo_user.token_auth)
        if len(site_list) == 1:
            return redirect(url_for('analytics_sites', idSite=site_list[0]['idsite']), 303)
        else:
            return render_template('analytics/sites_list.html', title='Behavee > Analytics > Site List',
                                   user=user, site_list=site_list, d=d, app=app, menuWebsitesList="active")

    if not site:
        abort(404)

    return render_template('analytics/sites.html', title='Behavee > Analytics > Site',
                           user=user, site=site, d=d, app=app, menuWebsitesList="active")


@app.route('/analytics/sites/add', methods=['GET', 'POST'])
@login_required
@partner_required
def analytics_sites_add():
    matomo_user = get_matomo_user()
    package_templates = PackageManager.list_templates(None)

    form = None
    form_class = partial(WebsiteForm.with_packages, [(p.id, p.name,) for p in package_templates])

    if request.method == 'POST':
        form = form_class(**request.form)
        if form.validate():
            data = form.data

            data['start_date'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            data['type_'] = 'website'
            data['user_login'] = matomo_user.login

            package_template_id = data.pop('package')

            try:
                r = SitesManager().addSite(app.config['MATOMO_ADMIN_TOKEN'], **data)
                flask.session['matomo_sites'] = SitesManager().getMatomoSites(app.config['MATOMO_ADMIN_TOKEN'])
            except MatomoError as e:
                flash(str(e), 'negative')
                return redirect('analytics/site')
            else:
                if 'value' in r:
                    PackageManager.add(r['value'], package_templates[package_template_id])
                    return redirect(f"/analytics/sites?idSite={r['value']}")

                # TODO add logging.warning

            return redirect('/analytics/sites')

    if form is None:
        form = form_class(
            sitesearch='1', ecommerce='1', website_currency='CZK', website_timezone='Europe/Prague'
        )

    return render_template('analytics/site_add.html',
                           title='Behavee > Analytics > Add Site', site_add_form=form, menuWebsitesAdd="active")


@app.route('/analytics/sites/<string:idsite>/edit', methods=['GET', 'POST'])
@login_required
@partner_required
def analytics_sites_edit(idsite):
    matomo_user = get_matomo_user()
    package_templates = PackageManager.list_templates(None)

    form = None
    form_class = partial(WebsiteForm.with_packages, [(p.id, p.name) for p in package_templates])

    site = SitesManager().getSiteFromId(matomo_user.token_auth, idsite)
    if not site:
        abort(404)

    if request.method == 'POST':
        form = form_class(**request.form)
        if form.validate():
            data = form.data
            package_template_id = data.pop('package')

            try:
                SitesManager().updateSite(matomo_user.token_auth, idsite, **data)
                flask.session['matomo_sites'] = SitesManager().getMatomoSites(app.config['MATOMO_ADMIN_TOKEN'])
            except MatomoError as e:
                # TODO log Matomo error
                flash(str(e), 'negative')
                pass
            else:
                PackageManager.update(idsite, package_templates[package_template_id])
                return redirect(f"/analytics/sites?idSite={idsite}")

            flash('There was an error updating your site. Please try again later', 'error')

    if form is None:
        form = form_class(**site)

    return render_template(
        'analytics/site_edit.html', title='Behavee > Analytics > Edit Site',
        site_edit_form=form, menuWebsitesList="active", idSite=site['idsite']
    )


@app.route('/analytics/sites/<string:idsite>/delete', methods=['GET', 'POST'])
@login_required
def analytics_sites_delete(idsite):
    form_class = SiteDeleteForm

    matomo_user = get_matomo_user()
    site = SitesManager().getSiteFromId(matomo_user.token_auth, idsite)

    if request.method == 'POST':
        form = form_class(formdata=request.form)
        if form.validate_on_submit():
            name = form.data['name'].strip()

            if site['name'] == name:
                try:
                    SitesManager().deleteSite(matomo_user.token_auth, idsite)
                    flask.session['matomo_sites'] = SitesManager().getMatomoSites(app.config['MATOMO_ADMIN_TOKEN'])
                except MatomoError as e:
                    flash(str(e), 'negative')
                else:
                    flash(f"Site '{site['name']}' was deleted")
                    return redirect(url_for('analytics_sites'))
            else:
                flash('Name does not match', 'negative')

    form = form_class()

    return render_template('analytics/site_delete.html',
                           title='Behavee > Analytics > Delete Site',
                           site_delete_form=form, menuWebsitesListList="active", idsite=idsite, site=site)