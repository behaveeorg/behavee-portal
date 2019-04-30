from functools import wraps
from typing import Union
from weakref import WeakKeyDictionary

from flask import request, redirect, url_for, flash
from flask_login import current_user

from app import app
from app.models.behavee import PartnerUserRelManager
from app.models.matomo import MatomoUser
from app.toolbox.matomo import UsersManager


_USER_CACHE = WeakKeyDictionary()


def get_matomo_user() -> Union[MatomoUser, None]:
    real_request = request._get_current_object()
    try:
        user = _USER_CACHE[real_request]
    except KeyError:
        try:
            user = MatomoUser.query.filter_by(email=current_user.email).first()
        except Exception:
            return None

        if user is None:
            UsersManager().addUser(current_user.email, app.config['MATOMO_ADMIN_TOKEN'])
            user = MatomoUser.query.filter_by(email=current_user.email).first()

        _USER_CACHE[real_request] = user

    assert user
    return user


def idsitehsr_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            idsitehsr = request.args['idSite']
        except KeyError:
            return redirect(url_for('analytics_heatmaps'), 303)

        # kwargs['idSite'] = site_id
        return func(*args, **kwargs)

    return wrapper

def partner_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_matomo_user()
        if not PartnerUserRelManager.get_partner(user.login):
            flash(f"Please, complete your profile first.", category='warning')
            return redirect(url_for('partner_edit_view'), 303)
        return func(*args, **kwargs)

    return wrapper
