from functools import wraps

from flask import url_for, request, render_template
from app import app, request
from app.toolbox.matomo import SitesManager
from app.toolbox.user import get_matomo_user


class SitePickerUrlBuilder:
    def __init__(self):
        self.request = request

    def __getitem__(self, item):
        args = dict(self.request.args)
        args.update(self.request.view_args)
        args['idSite'] = item
        return url_for(self.request.endpoint, **args)


@app.context_processor
def current_site_processor():
    context = {'current_site': None}

    idsite = request.args.get('idSite')
    if idsite:
        user = get_matomo_user()
        if user:
            site = SitesManager().getSiteFromId(user.token_auth, idsite)

            args = dict(request.args)
            args.pop('idSite')
            args.update(request.view_args)
            site['picker_url'] = url_for(request.endpoint, **args)
            context['current_site'] = site

    return context


def idsite_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.args.get('idSite', '').strip():
            user = get_matomo_user()
            if user:
                sites = SitesManager().getMatomoSites(user.token_auth)
                return render_template('sites_picker.html', next_url=SitePickerUrlBuilder(), site_list=sites)

        return func(*args, **kwargs)

    return wrapper