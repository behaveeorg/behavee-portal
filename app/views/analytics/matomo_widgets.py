from flask_security import login_required
from app.models.security import User
from app.models.matomo import *
from app.toolbox.current_site import idsite_required
from app.toolbox.user import get_matomo_user
from flask import request
from datetime import date

@app.route('/analytics/visitors/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_visitors(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/visitors.html', title='Behavee > Analytics > Visitors',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsVisitors="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/behaviour/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_behaviour(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/behaviour.html', title='Behavee > Analytics > Behaviour',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsBehaviour="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/acquisition/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_acquisition(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/acquisition.html', title='Behavee > Analytics > Acquisition',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsAcquisition="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/campaigns/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_campaigns(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/campaigns.html', title='Behavee > Analytics > Campaigns',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsAcquisition="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/ecommerce/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_ecommerce(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]
    return render_template('analytics/ecommerce.html', title='Behavee > Analytics > Ecommerce',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsEcommerce="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/products/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_products(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/products.html', title='Behavee > Analytics > Products',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsProducts="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/sales/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_sales(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/sales.html', title='Behavee > Analytics > Sales',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsSales="active",
                           request_period=request_period,
                           request_date=request_date)


@app.route('/analytics/goals/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_goals(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/goals.html', title='Behavee > Analytics > Goals',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsGoals="active",
                           request_period=request_period,
                           request_date=request_date)

@app.route('/analytics/funnels/<string:action>/', methods=['GET'])
@login_required
@idsite_required
def analytics_funnels(action):
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/funnels.html', title='Behavee > Analytics > Funnels',
                           user=user, pageAction=action, d=d, app=app, menuAnalyticsGoals="active",
                           request_period=request_period,
                           request_date=request_date)

@app.route('/analytics/seo/', methods=['GET'])
@login_required
@idsite_required
def analytics_seo():
    d = {}
    user = User.query.filter_by(email=current_user.email).first()
    d['current_login_at'] = user.current_login_at.strftime("%Y-%m-%d %H:%M:%S")
    d['last_login_at'] = user.last_login_at.strftime("%Y-%m-%d %H:%M:%S")

    matomo_user = get_matomo_user()

    request_period = request.args.get('period', 'month')
    request_date = request.args.get('date', str(date.today()))
    if request_period == 'week':
        request_date = request_date.split(',')
        request_date = request_date[0]

    return render_template('analytics/seo.html', title='Behavee > Analytics > SEO',
                           user=user, pageAction=None, d=d, app=app, menuAnalyticsSeo="active",
                           request_period=request_period,
                           request_date=request_date)