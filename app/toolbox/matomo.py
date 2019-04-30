from json import JSONDecodeError

from app.models.matomo import *

from os import urandom
from urllib.parse import urlencode
from app import session, flask


class MatomoError(Exception):
    def __init__(self, response):
        assert 'result' in response and response['result'] == 'error'

        self.response = response
        super().__init__(response.get('message', 'Message not supplied'))



class MatomoError(Exception):
    def __init__(self, response):
        assert 'result' in response and response['result'] == 'error'

        self.response = response
        super().__init__(response.get('message', 'Message not supplied'))


class MatomoAnalytics(object):
    """
    The Matomo analytics API class
    """
    def __init__(self, *, raise_exception=True):
        self.p = {}
        self.list_p = {}
        self.set_parameter('module', value='API')
        self.set_format('json')
        self.api_url = app.config['MATOMO_API_URL']
        self.raise_exception = raise_exception

    @staticmethod
    def _build_key(*parts):
        key = parts[0]
        for i in range(1, len(parts)):
            key = f'{key}[{parts[i]}]'

        return key

    def set_parameter(self, *keys, value):
        # assert key not in self.list_p, '{} already set as list parameter'.format(key)
        # self.p[key] = str(value)
        key = self._build_key(*keys)
        self.p[key] = str(value)

    def remove_parameter(self, *keys):
        key = self._build_key(*keys)
        if key in self.p:
            del self.p[key]

    def get_parameter(self, *keys, default=None):
        return self.p.get(self._build_key(*keys), default)

    def set_method(self, method):
        self.set_parameter('method', value=method)

    def set_idsite(self, id_site):
        self.set_parameter('idSite', value=id_site)

    def set_token_auth(self, token):
        self.set_parameter('token_auth', value=token)

    def set_date(self, date):
        self.set_parameter('date', value=date)

    def set_period(self, period):
        self.set_parameter('period', value=period)

    def set_format(self, format_):
        self.set_parameter('format', value=format_)

    def set_filter_limit(self, filter_limit):
        self.set_parameter('filter_limit', value=filter_limit)

    def set_api_url(self, api_url):
        self.api_url = api_url

    def set_segment(self, segment):
        self.set_parameter('segment', value=segment)

    def get_query_string(self):
        if self.api_url is None:
            raise ConfigurationError("API URL not set")

        qs = ''

        if len(self.p):
            params = self.p.copy()
            for key, item_list in self.list_p.items():
                for i, item in enumerate(item_list):
                    params[f'{key}[{i}]'] = item

            qs = self.api_url
            qs += '?'
            qs += urlencode(self.p)

        return qs

    def get_query_params(self):
        params = {}

        for key, value in self.p.items():
            params[key] = quote_plus(value)

        for key, item_list in self.list_p.items():
            for i, item in enumerate(item_list):
                params[f'{key}[{i}]'] = quote_plus(item)

        return params

    def send_request(self, *, raise_exception=None):
        raise_exception = raise_exception if raise_exception is not None else self.raise_exception

        headers = {'Accept': 'application/json'}
        params = self.get_query_params()
        assert 'method' in params
        assert 'token_auth' in params

        with requests.Session() as s1:
            req = requests.Request('GET', self.api_url, headers=headers).prepare()

            if params:
                params_str = '&'.join(f'{k}={v}' for k, v in params.items())
                req.url = f'{req.url}?{params_str}'

            resp = s1.send(req, verify=True, timeout=10)

            try:
                r = resp.json(strict=False)
            except JSONDecodeError:
                # TODO what to do if BODY is not JSON
                raise

            # r = json.loads(resp.content.decode('utf-8'), strict=False)

            if raise_exception and 'result' in r and r['result'] == 'error':
                raise MatomoError(r)

            return r


class InvalidParameter(Exception):
    # Todo add logging
    pass


class ConfigurationError(Exception):
    # Todo add logging
    pass


class SitesManager(MatomoAnalytics):
    def __init__(self):
        super(SitesManager, self).__init__()

    def getSitesWithAtLeastViewAccess(self, token_auth):
        self.set_token_auth(token_auth)
        self.set_method('SitesManager.getSitesWithAtLeastViewAccess')
        return self.send_request()

    def getSitesIdWithAdminAccess(self, token_auth):
        self.set_token_auth(token_auth)
        self.set_method('SitesManager.getSitesIdWithAdminAccess')
        return self.send_request()

    def getMatomoSites(self, token_auth):
        self.set_token_auth(token_auth)
        r = self.getSitesWithAtLeastViewAccess(token_auth)
        return r

    def addSite(self, token_auth, *, name, type_, main_url, user_login, ecommerce='', sitesearch='', start_date='',
                sitesearch_keyword_parameters=None, sitesearch_category_parameters=None, excluded_ips=None,
                excluded_parameters=None, timezone='', currency='', group='', excluded_user_agents=None,
                keep_url_fragments='', exclude_unknown_urls=''):

        self.set_method('SitesManager.addSite')
        self.set_token_auth(token_auth)

        self.set_parameter('siteName', value=name)
        # self.set_list_parameter('urls', [main_url])
        self.set_parameter('urls', 0, value=main_url)
        self.set_parameter('ecommerce', value=ecommerce)
        self.set_parameter('siteSearch', value=sitesearch)
        # self.set_list_parameter('searchKeywordParameters', sitesearch_keyword_parameters, join=True)
        self.set_parameter('searchKeywordParameters', value=','.join(sitesearch_keyword_parameters))
        # self.set_list_parameter('searchCategoryParameters', sitesearch_category_parameters, join=True)
        self.set_parameter('searchCategoryParameters', value=','.join(sitesearch_category_parameters))
        # self.set_list_parameter('excludedIps', excluded_ips, join=True)
        self.set_parameter('excludedIps', value=','.join(excluded_ips))
        # self.set_list_parameter('excludedQueryParameters', excluded_parameters, join=True)
        self.set_parameter('excludedQueryParameters', value=','.join(excluded_parameters))
        self.set_parameter('timezone', value=timezone)
        self.set_parameter('currency', value=currency)
        #self.set_parameter('group', group)
        self.set_parameter('startDate', value=start_date)
        # self.set_list_parameter('excludedUserAgents', excluded_user_agents, join=True)
        self.set_parameter('excludedUserAgents', value=','.join(excluded_user_agents))
        self.set_parameter('excludeUnknownUrls', value=exclude_unknown_urls)
        self.set_parameter('keepURLFragments', value=keep_url_fragments)
        self.set_parameter('type', value=type_)

        r = self.send_request()

        if 'value' in r:
            UsersManager().setUserAccess(token_auth, user_login, 'admin', r['value'])

        return r

    # def updateSite(self, token_auth, siteId, *, name, urls=None, ecommerce='', sitesearch='',
    #                searchKeywordParameters = None, searchCategoryParameters = None, excludedIps = None,
    #                excludedQueryParameters = None, timezone = '', currency = '', group = '', startDate = '',
    #                excludedUserAgents = None, keep_url_fragments='', type = '', settingValues = '',
    #                excludeUnknownUrls = '', userLogin=''):

    def updateSite(self, token_auth, idsite, *, name, main_url, ecommerce='', sitesearch='',
                   sitesearch_keyword_parameters=None, sitesearch_category_parameters=None, excluded_ips=None,
                   excluded_parameters=None, timezone='', currency='', group='', excluded_user_agents=None,
                   keep_url_fragments='', exclude_unknown_urls=''):

        self.set_method('SitesManager.updateSite')
        self.set_idsite(idsite)
        self.set_token_auth(token_auth)

        self.set_parameter('siteName', value=name)
        # self.set_list_parameter('urls', [main_url])
        self.set_parameter('urls', 0, value=main_url)
        self.set_parameter('ecommerce', value=ecommerce)
        self.set_parameter('siteSearch', value=sitesearch)
        self.set_parameter('keepURLFragments', value=keep_url_fragments)
        self.set_parameter('searchKeywordParameters', value=','.join(sitesearch_keyword_parameters))
        self.set_parameter('searchCategoryParameters', value=','.join(sitesearch_category_parameters))
        self.set_parameter('excludedIps', value=','.join(excluded_ips))
        self.set_parameter('excludedQueryParameters', value=','.join(excluded_parameters))
        self.set_parameter('timezone', value=timezone)
        self.set_parameter('currency', value=currency)
        # self.set_parameter('group', group)
        # self.set_list_parameter('excludedUserAgents', excluded_user_agents, join=True)
        self.set_parameter('excludedUserAgents', value=','.join(excluded_user_agents))
        self.set_parameter('excludeUnknownUrls', value=exclude_unknown_urls)

        return self.send_request()

    def deleteSite(self, token_auth, idSite):
        # check, if user has write access to site
        self.set_method('SitesManager.getSitesIdWithAdminAccess')
        self.set_token_auth(token_auth)
        r = self.send_request()

        if idSite in r:
            self.set_method('SitesManager.deleteSite')
            self.set_token_auth(app.config['MATOMO_ADMIN_TOKEN'])
            self.set_parameter('idSite', value=idSite)
            r = self.send_request()
            return r
        else:
            return {'result': 'error', 'message': "Insufficient privileges or site doesn't exists."}

    def getSiteFromId(self, token_auth, idSite):
        self.set_token_auth(token_auth)
        self.set_method('SitesManager.getSiteFromId')
        self.set_parameter('idSite', value=idSite)

        try:
            return self.send_request()[0]
        except (IndexError, MatomoError):
            # TODO log MatomoError
            return None


class UsersManager(MatomoAnalytics):
    def __init__(self):
        super(UsersManager, self).__init__()

    def getUserByEmail(self):
        self.set_method('UsersManager.getUserByEmail')
        return self.send_request()

    def addUser(self, email, token_auth):
        portal_login = email
        portal_email = email
        portal_password = urandom(32).hex()   # random password

        self.set_token_auth(token_auth)
        self.set_method('UsersManager.addUser')

        self.set_parameter('userLogin', value=portal_login)
        self.set_parameter('email', value=portal_email)
        self.set_parameter('password', value=portal_password)
        self.set_parameter('alias', value=portal_login)
        self.set_parameter('initialIdSite', value='')

        return self.send_request()

    def setUserAccess(self, token_auth, userLogin, access, idSites):
        self.set_method('UsersManager.setUserAccess')
        self.set_token_auth(token_auth)

        self.set_parameter('userLogin', value=userLogin)
        self.set_parameter('access', value=access)
        self.set_parameter('idSites', value=idSites)

        return self.send_request()


class HeatmapSessionRecordingManager(MatomoAnalytics):
    def set_idsitehsr(self, value):
        self.set_parameter('idSiteHsr', value=value)

    def addHeatmap(self, token_auth, idsite, *, name, match_page_rules, sample_limit='1000', sample_rate='5',
                   excluded_elements=None, screenshot_url='', breakpoint_mobile='', breakpoint_tablet=''):

        self.set_method('HeatmapSessionRecording.addHeatmap')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)

        self.set_parameter('name', value=name)
        self.set_parameter('sampleLimit', value=sample_limit)
        self.set_parameter('sampleRate', value=sample_rate)
        self.set_parameter('excludedElements', value=','.join(excluded_elements))
        self.set_parameter('screenshotUrl', value=screenshot_url)
        self.set_parameter('breakpointMobile', value=breakpoint_mobile)
        self.set_parameter('breakpointTablet', value=breakpoint_tablet)

        for rule_index, rule in enumerate(match_page_rules):
            for rule_key, rule_value in rule.items():
                self.set_parameter('matchPageRules', rule_index, rule_key, value=rule_value)

        return self.send_request()

    def getHeatmaps(self, token_auth, idsite):
        self.set_method('HeatmapSessionRecording.getHeatmaps')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)

        return self.send_request()

    def getHeatmap(self, token_auth, idsite, idsitehsr):
        self.set_method('HeatmapSessionRecording.getHeatmap')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)
        self.set_idsitehsr(idsitehsr)

        return self.send_request()

    def deleteHeatmap(self, token_auth, idsite, idsitehsr):
        self.set_method('HeatmapSessionRecording.deleteHeatmap')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)
        self.set_idsitehsr(idsitehsr)

        return self.send_request()

    def updateHeatmap(self, token_auth, *, idsite, idsitehsr, name, match_page_rules, sample_limit=1000,
                      sample_rate=5.0, excluded_elements=None, screenshot_url='', breakpoint_mobile='',
                      breakpoint_tablet=''):

        self.set_method('HeatmapSessionRecording.updateHeatmap')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)
        self.set_idsitehsr(idsitehsr)

        self.set_parameter('name', value=name)
        self.set_parameter('sampleLimit', value=sample_limit)
        self.set_parameter('sampleRate', value=sample_rate)
        self.set_parameter('excludedElements', value=','.join(excluded_elements))
        self.set_parameter('screenshotUrl', value=screenshot_url)
        self.set_parameter('breakpointMobile', value=breakpoint_mobile)
        self.set_parameter('breakpointTablet', value=breakpoint_tablet)

        for rule_index, rule in enumerate(match_page_rules):
            for rule_key, rule_value in rule.items():
                self.set_parameter('matchPageRules', rule_index, rule_key, value=rule_value)

        return self.send_request()

    def getSessionRecordings(self, token_auth, idsite):
        self.set_method('HeatmapSessionRecording.getSessionRecordings')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)

        return self.send_request()

    def getSessionRecording(self, token_auth, idsite, idsitehsr):
        self.set_method('HeatmapSessionRecording.getSessionRecording')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)
        self.set_idsitehsr(idsitehsr)

        return self.send_request()

    def addSessionRecording(self, token_auth, *, idsite, name, match_page_rules, sample_limit='1000', sample_rate='5',
                            min_session_time='', requires_activity='', capture_keystrokes=''):

        self.set_method('HeatmapSessionRecording.addSessionRecording')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)

        self.set_parameter('name', value=name)
        self.set_parameter('sampleLimit', value=sample_limit)
        self.set_parameter('sampleRate', value=sample_rate)
        self.set_parameter('minSessionTime', value=min_session_time)
        self.set_parameter('requiresActivity', value=requires_activity)
        self.set_parameter('captureKeystrokes', value=capture_keystrokes)

        for rule_index, rule in enumerate(match_page_rules):
            for rule_key, rule_value in rule.items():
                self.set_parameter('matchPageRules', rule_index, rule_key, value=rule_value)

        return self.send_request()

    def updateSessionRecording(self, token_auth, *, idsite, idsitehsr, name, match_page_rules, sample_limit='1000',
                               sample_rate='5', min_session_time='', requires_activity='', capture_keystrokes=''):

        self.set_method('HeatmapSessionRecording.updateSessionRecording')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)
        self.set_idsitehsr(idsitehsr)

        self.set_parameter('name', value=name)
        self.set_parameter('sampleLimit', value=sample_limit)
        self.set_parameter('sampleRate', value=sample_rate)
        self.set_parameter('minSessionTime', value=min_session_time)
        self.set_parameter('requiresActivity', value=requires_activity)
        self.set_parameter('captureKeystrokes', value=capture_keystrokes)

        for rule_index, rule in enumerate(match_page_rules):
            for rule_key, rule_value in rule.items():
                self.set_parameter('matchPageRules', rule_index, rule_key, value=rule_value)

        return self.send_request()

    def deleteSessionRecording(self, token_auth, idsite, idsitehsr):
        self.set_method('HeatmapSessionRecording.deleteHeatmap')
        self.set_token_auth(token_auth)
        self.set_idsite(idsite)
        self.set_idsitehsr(idsitehsr)

        return self.send_request()

########################################################
### register new matomo user

# def register_matomo_user():
#     # Matomo API:
#     # UsersManager.userEmailExists (userEmail) [ No example available ]
#     # UsersManager.addUser (userLogin, password, email, alias = '', initialIdSite = '')
#
#     #guid = uuid.uuid4()
#     portal_login = current_user.email
#     portal_email = current_user.email
#     portal_password = secrets.token_urlsafe(32) #random password
#
#     #set default headers and auth method
#     headers = {'Accept': 'application/json'}
#
#     s1 = requests.Session()
#     query = app.config['MATOMO_API_URL'] + \
#             '?module=API' \
#             '&method=UsersManager.addUser' \
#             '&format=json' \
#             '&userLogin=' + urllib.parse.quote_plus(str(portal_login)) + \
#             '&password=' + urllib.parse.quote_plus(str(portal_password)) + \
#             '&email=' + urllib.parse.quote_plus(str(portal_email)) + \
#             '&alias=' + urllib.parse.quote_plus(str(portal_login)) + \
#             '&initialIdSite=' \
#             '&token_auth=' + urllib.parse.quote_plus(app.config['MATOMO_ADMIN_TOKEN'])
#
#     try:
#         resp0 = s1.get(query, headers=headers, verify=True, timeout=10)
#         if resp0.status_code == 200:
#             r = json.loads(resp0.content.decode('utf-8'), strict=False)
#             for item in r:
#                 print(item)
#             s1.close()
#         else:
#             e = BadRequest('Error')
#             e.code = resp0.status_code
#             e.data = {'value': 'API error'}
#             s1.close()
#             raise e
#     except:
#         pass


# def register_matomo_site(data, matomo_login):
#     # Matomo API:
#     # - first create site with superuser token
#     # SitesManager.addSite (siteName, urls = '', ecommerce = '', siteSearch = '',
#     # searchKeywordParameters = '', searchCategoryParameters = '', excludedIps = '',
#     # excludedQueryParameters = '', timezone = '', currency = '', group = '', startDate = '',
#     # excludedUserAgents = '', keepURLFragments = '', type = '', settingValues = '',
#     # excludeUnknownUrls = '')
#     # - then create access for new site
#     # UsersManager.setUserAccess(userLogin, access, idSites)
#
#     #set default headers and auth method
#     headers = {'Accept': 'application/json'}
#
#     #try:
#     s1 = requests.Session()
#     query = app.config['MATOMO_API_URL'] + \
#             '?module=API' \
#             '&method=SitesManager.addSite' \
#             '&format=json' \
#             '&siteName=' + urllib.parse.quote_plus(str(data['website_name'])) + \
#             '&urls=' + urllib.parse.quote_plus(str(data['website_url'])) + \
#             '&ecommerce=' + urllib.parse.quote_plus(str(data['website_ecommerce'])) + \
#             '&siteSearch=' + urllib.parse.quote_plus(str(data['website_sitesearch'])) + \
#             '&excludedIps=' + urllib.parse.quote_plus(str(data['website_excluded_ips'])) + \
#             '&excludedQueryParameters=' + urllib.parse.quote_plus(str(data['website_excluded_parameters'])) + \
#             '&excludedUserAgents=' + urllib.parse.quote_plus(str(data['website_excluded_useragents'])) + \
#             '&timezone=' + urllib.parse.quote_plus(str(data['website_timezone'])) + \
#             '&currency=' + urllib.parse.quote_plus(str(data['website_currency'])) + \
#             '&token_auth=' + urllib.parse.quote_plus(app.config['MATOMO_ADMIN_TOKEN'])
#     resp0 = s1.get(query, headers=headers, verify=True, timeout=10)
#
#     if resp0.status_code == 200:
#         r = json.loads(resp0.content.decode('utf-8'), strict=False)
#         if 'result' in r:
#             if r['result'] == 'error':
#                 flash(r['message'], 'negative')
#                 return redirect('analytics/site')
#         elif 'value' in r:
#             new_idsite = r['value']
#         else:
#             flash('Unknown response', 'negative')
#             return redirect('analytics/site')
#     else:
#         e = BadRequest('Error')
#         e.code = resp0.status_code
#         e.data = {'value': 'API error'}
#         s1.close()
#         raise e
#
#     query = app.config['MATOMO_API_URL'] + \
#             '?module=API' \
#             '&method=UsersManager.setUserAccess' \
#             '&format=json' \
#             '&userLogin=' + urllib.parse.quote_plus(str(matomo_login)) + \
#             '&access=view' + \
#             '&idSites=' + urllib.parse.quote_plus(str(new_idsite)) + \
#             '&token_auth=' + app.config['MATOMO_ADMIN_TOKEN']
#     resp0 = s1.get(query, headers=headers, verify=True, timeout=10)
#
#     if resp0.status_code == 200:
#         r = json.loads(resp0.content.decode('utf-8'), strict=False)
#         if 'result' in r:
#             if r['result'] == 'error':
#                 flash(r['message'], 'negative')
#                 return redirect('analytics/site')
#         elif 'value' in r:
#             flash('Site was created', 'positive')
#         else:
#             flash('Unknown response', 'negative')
#             s1.close()
#             return redirect('analytics/site')
#         s1.close()
#     else:
#         e = BadRequest('Error')
#         e.code = resp0.status_code
#         e.data = {'value': 'API error'}
#         s1.close()
#         raise e
#
#     #except:
#     #    pass