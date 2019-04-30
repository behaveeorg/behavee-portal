#!/usr/bin/env python3
import time
from threading import Thread
import flask
from flask import Flask, redirect, url_for, session, request, jsonify, render_template, g
from flask_session import Session
from flask_security import Security, SQLAlchemyUserDatastore
import flask_admin
from flask_admin.base import MenuLink
from flask_admin import helpers as admin_helpers
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_oauthlib.client import OAuth, OAuthException
from jose import jws
import json
import requests
import uuid
import logging

#  Create app
app = Flask(__name__)

# Configurations
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']

from flask_cors import CORS, cross_origin
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

oauth = OAuth(app)

logger = logging.getLogger(__name__)

# === Microsoft B2C AD    ===========
tenant_id = app.config['MICROSOFT_TENANT_ID']
client_id = app.config['MICROSOFT_CLIENT_ID']
client_secret = app.config['MICROSOFT_CLIENT_SECRET']
policy_name = app.config['MICROSOFT_POLICY_NAME']
# ===================================
scopes = 'openid ' + client_id
core_url = 'https://login.microsoftonline.com/tfp/' + tenant_id + '/' + policy_name
token_url = core_url + '/oauth2/v2.0/token'
authorize_url = core_url + '/oauth2/v2.0/authorize'
keys_url = core_url + '/discovery/keys'

# This sample loads the keys on boot, but for production
# the keys should be refreshed either periodically or on
# jws.verify fail to be able to handle a key rollover

keys_raw = requests.get(keys_url).text
keys = json.loads(keys_raw)

# Put your consumer key and consumer secret into a config file
# and don't check it into github!!
microsoft = oauth.remote_app(
    'microsoft',
    consumer_key=client_id,
    consumer_secret=client_secret,
    request_token_params={'scope': scopes},
    base_url='http://ignore',  # We won't need this
    request_token_url=None,
    access_token_method='POST',
    access_token_url=token_url,
    authorize_url=authorize_url
)


@microsoft.tokengetter
def get_microsoft_oauth_token():
    return flask.session.get('microsoft_token')


# Database
db = SQLAlchemy(app)
# Sessions
app.config['SESSION_SQLALCHEMY'] = db
session = Session(app)
session.app.session_interface.db.create_all()

# Load models
from app.models.security import *
from app.views.security import *

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# Proxy fix for non https connections (e.g. swagger.json)
from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

# Setup the password crypting
bcrypt = Bcrypt(app)

# Setup the mail server
mail = Mail(app)

# Import the views
from app.views import main, user, error
from app.views.account import profile, partner
from app.views.analytics import sites, tracking_code, matomo_widgets, session_recordings
from app.views.reports import visits
from app.toolbox import date_picker, url as toolbox_url


app.register_blueprint(user.userbp)

# Load API
from app.api.restplus import api

# Create flask admin
admin = flask_admin.Admin(app, 'Behavee portal admin', base_template='my_master.html', template_mode='bootstrap3', )

# Add views
admin.add_link(MenuLink(name='API browser', url='/api', category='API', class_name="nav navbar-nav", target="_blank"))


from flask_security import user_registered
@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    default_role = user_datastore.find_role("user")
    user_datastore.add_role_to_user(user, default_role)
    db.session.commit()


@app.before_request
def detect_user():
    # detect only non static requests for authenticated users
    if request.url_rule is not None \
            and request.url_rule.rule != "/static/<path:filename>" \
            and not request.url_rule.rule.startswith("/swagger") \
            and not request.url_rule.rule.startswith("/api") \
            and current_user.is_authenticated:
        from app import session
        from app.models.matomo import MatomoUser
        from app.toolbox.matomo import SitesManager, UsersManager

        g.idSite = request.args.get("idSite")
        # first get user from Matomo database, because of unknown token_auth
        matomo_user = MatomoUser.query.filter_by(email=current_user.email).first()
        if matomo_user is None:
            m = UsersManager()
            r = m.addUser(current_user.email, app.config['MATOMO_ADMIN_TOKEN'])
            matomo_user = MatomoUser.query.filter_by(email=current_user.email).first()

        if 'matomo_token_auth' not in flask.session:
            flask.session['matomo_token_auth'] = matomo_user.token_auth
        if 'matomo_sites' not in flask.session:
            s = SitesManager()
            flask.session['matomo_sites'] = s.getMatomoSites(flask.session['matomo_token_auth'])
        if g.idSite is None and flask.session['matomo_sites']:
            g.idSite = flask.session['matomo_sites'][0]['idsite']


# run server
def run():
    # import namespaces
    from app.api.visitor.endpoints.visitor import ns as visitor_namespace
    from app.api.behavee.endpoints.behavee import ns as behavee_namespace

    blueprint = Blueprint('api', __name__)
    api.init_app(blueprint)

    # add API namespaces
    api.add_namespace(visitor_namespace)
    api.add_namespace(behavee_namespace)
    app.register_blueprint(blueprint, url_prefix=app.config['FLASK_API_URL_PREFIX'])

    # Here we patch the application
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    db = SQLAlchemy(app)
    db.init_app(app)

    host = app.config['FLASK_SERVER_HOST']
    port = app.config['FLASK_SERVER_PORT']
    debug = app.config['FLASK_DEBUG']

    app.run(host=host, port=port, debug=debug)