import flask
from flask import render_template, redirect, request, url_for,g
from app import app, db, session, uuid, microsoft, jws, keys, cross_origin, logger
from flask_login import login_user, logout_user
from app.models.security import *
from app.models.matomo import *
from app.models.microsoft_ad import *
from app.toolbox.matomo import SitesManager, UsersManager
import json
from datetime import datetime
from app.models.behavee import *
from datetime import date

from flask import make_response
from app.toolbox.current_site import idsite_required


@app.route('/')
@cross_origin()
@idsite_required
def index():
    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    if current_user.is_authenticated:
        return render_template('index.html', title='Behavee portal', app=app, g=g, session=flask.session, menuDashboard="active",
                               request_period=request_period,
                               request_date=request_date)
    else:
        return render_template('index_login.html', title='Behavee portal', app=app, idSite=None, session=None, menuDashboard="active",
                               request_period=request_period,
                               request_date=request_date)

@app.route('/api')
def api():
    return redirect(app.config['FLASK_API_URL_PREFIX'])


@app.route('/users/login', methods=['POST', 'GET'])
def users_login():
    #if 'microsoft_token' in flask.session:
    #s    return redirect(url_for('index'))

    # Generate the guid to only accept initiated logins
    guid = uuid.uuid4()
    flask.session['state'] = guid
    return microsoft.authorize(callback=url_for('users_authorized', _external=True, _scheme=app.config['PREFERRED_URL_SCHEME']), state=guid)


@app.route('/users/logout', methods=['POST', 'GET'])
def users_logout():
    flask.session.pop('microsoft_token', None)
    flask.session.pop('claims', None)
    flask.session.pop('state', None)
    flask.session.pop('matomo_token_auth', None)
    flask.session.pop('matomo_sites', None)
    logout_user()
    return redirect(url_for('index'))

#@app.route('/users/login/authorized') #ToDo change path in Azure AD app
@app.route('/user/login/authorized')
def users_authorized():
    response = microsoft.authorized_response()

    if response is None:
        # user wants to change his password
        if 'AADB2C90118' in request.args.get('error_description', default=''):

            tenant_id = app.config['MICROSOFT_TENANT_ID']
            client_id = app.config['MICROSOFT_CLIENT_ID']
            policy_name = app.config['MICROSOFT_POLICY_NAME_PWD_RESET']

            reset_password_url = 'https://login.microsoftonline.com/' + tenant_id + \
                                 '/oauth2/v2.0/authorize?p=' + policy_name + \
                                 '&client_id=' + client_id + \
                                 '&nonce=defaultNonce&redirect_uri=' + url_for('users_authorized', _external=True, _scheme=app.config['PREFERRED_URL_SCHEME']) + \
                                 '&scope=openid&response_type=id_token&prompt=login'
            return(redirect(reset_password_url))

        e = request.args.get('error', default=None)
        d =  request.args.get('error_description', 'No description supplied')
        if e is not None:
            flash('Access Denied: Reason=' + e + ', Error='+ d, 'negative')
            return redirect(url_for('index'))
        else:
            return redirect(url_for('users_login'))

    # Check response for state
    if str(flask.session['state']) != str(request.args['state']):
        # ToDo add logging here
        raise Exception('State has been messed with, end authentication')

    # Okay to store this in a local variable, encrypt if it's going to client
    # machine or database. Treat as a password.
    access_token = response['access_token']
    flask.session['microsoft_token'] = (access_token, '')
    verified = jws.verify(access_token, keys, algorithms=['RS256'])
    claims = json.loads(verified.decode('utf-8'))

    dt_now = datetime.now()
    claim = Claims(dt=dt_now, claim=str(json.dumps(claims)), access_token=str(access_token))
    try:
        db.session.add(claim)
        db.session.commit()
    except Exception:
        # ToDo add logging here
        db.session.rollback()

    session_email = None
    session_family_name = None
    session_given_name = None

    if 'family_name' in claims:
        session_family_name = claims['family_name']

    if 'given_name' in claims:
        session_given_name = claims['given_name']

    if 'emails' in claims:
        session_email = claims['emails'][0]

        portal_user = User.query.filter_by(email=session_email).first()
        if portal_user is None:
            register_portal_user(session_email, session_given_name, session_family_name)
            portal_user = User.query.filter_by(email=session_email).first()
            try:
                # find default role
                default_role = Role.query.filter_by(name='user').first()
                from sqlalchemy import insert
                stmt = RolesUsers.insert().values(user_id=portal_user.id, role_id=default_role.id)
            except:
                # ToDo add logging here
                pass
            db.session.commit()
            if portal_user is None:
                # ToDo add logging here
                raise NotImplementedError

        try:
            login_user(portal_user)
        except Exception as err:
            # ToDo add logging here
            print("Error {}".format(err))

        # first get user from Matomo database, because of unknown token_auth
        matomo_user = MatomoUser.query.filter_by(email=current_user.email).first()
        if matomo_user is None:
            try:
                m = UsersManager()
                r = m.addUser(current_user.email, app.config['MATOMO_ADMIN_TOKEN'])
                db.session.commit()
                matomo_user = MatomoUser.query.filter_by(email=current_user.email).first()
            except Exception as err:
                # ToDo add logging here
                print("Error {}".format(err))
                pass

        if 'matomo_token_auth' not in flask.session:
            try:
                flask.session['matomo_token_auth'] = matomo_user.token_auth
            except Exception as err:
                # ToDo add logging here
                print("Error {}".format(err))
                pass

        if 'matomo_sites' not in flask.session:
            try:
                s = SitesManager()
                flask.session['matomo_sites'] = s.getMatomoSites(flask.session['matomo_token_auth'])
            except Exception as err:
                # ToDo add logging here
                print("Error {}".format(err))
                pass

    return redirect(url_for('index'))
