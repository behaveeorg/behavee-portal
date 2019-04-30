from app import db
import app.config
import mysql.connector
from werkzeug.exceptions import BadRequest
import time
from app.api.behavee.parsers import e401, e404, e500

config = {
    'user': app.config.MATOMO_DATABASE_USER,
    'password': app.config.MATOMO_DATABASE_PASS,
    'host': app.config.MATOMO_DATABASE_HOST,
    'port': app.config.MATOMO_DATABASE_PORT,
    'database': app.config.MATOMO_DATABASE_NAME,
    'connection_timeout': 5,
}

def authorize(token_auth):
    '''
    :param token_auth: user's autentication token
    :return: boolean - if token is in database
    '''
    try:
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        # query matomo database with token_auth and return user login
        query = 'SELECT du.login FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`user` du WHERE du.token_auth=\'' + token_auth + '\''

        cur.execute(query)
        login = cur.fetchall()

        # if user login exist then given token_auth is in database
        if len(login) > 0:
            return True
        else:
            return False

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'value': 'Error'}
        raise e


def get_user_login(token_auth):
    '''
    :param token_auth: user's autentication token
    :return: user's login if token is in database, None if user is not in database
    '''
    try:
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        # query matomo database with token_auth and return user login
        query = 'SELECT du.login FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`user` du WHERE du.token_auth=\'' + token_auth + '\''

        cur.execute(query)
        login = cur.fetchall()

        # if user login exist then given token_auth is in database
        if len(login) > 0:
            return login[0][0]
        else:
            return None

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'value': 'Error'}
        raise e


def get_matomo_visitors(limit, token_auth):
    '''
    :param limit: limit number for db query
    :return: a list of n visitors
    '''
    try:
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        get_sites = 'SELECT idsite FROM ' \
            '`' + app.config.MATOMO_DATABASE_NAME + '`.`access` da ' \
            'LEFT JOIN`' + app.config.MATOMO_DATABASE_NAME + '`.`user` du ' \
            'ON da.login = du.login ' \
            'WHERE du.token_auth=\'' + token_auth + '\' '

        cur.execute(get_sites)
        sites = tuple(r[0] for r in cur.fetchall())

        visitors =  'SELECT DISTINCT hex(lv.idvisitor) ' \
                    'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                    'WHERE lv.idsite IN '+str(sites)+' ' \
                    'ORDER BY lv.idvisit ' \
                    'LIMIT ' + str(limit - 100) + ',' + str(100) + ' '

        cur.execute(visitors)
        visitors = tuple(r[0] for r in cur.fetchall())

        return visitors


        # TODO: more info about visitors: currently unused
        # query = 'SELECT DISTINCT hex(lv.idvisitor), lv.visit_last_action_time, lv.visit_first_action_time ' \
        #         'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
        #         'WHERE hex(lv.idvisitor) IN '+str(visitors)+'' \
        #         'ORDER BY lv.idvisit '
        #
        # cur.execute(query)
        # data = cur.fetchall()
        #
        # cur.close()
        # cnx.close()
        # print(len(data))
        # print('function took: ' + str(round(time.time() - start_time, 5)) + ' sec.')


    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'value': 'Error'}
        raise e


def get_matomo_visitor_geolocation_device(visitorid):
    '''
    :param visitorid: id of visitor which data will be returned
    :return: dictionary with visitor geolocation data, visitor device data
    '''

    try:
        query = 'SELECT DISTINCT lv.visit_first_action_time, lv.visit_last_action_time, ' \
                'lv.location_country, lv.location_city, lv.location_latitude, ' \
                'lv.location_longitude, lv.config_device_model, lv.config_device_brand, ' \
                'lv.config_device_type, lv.config_os, lv.config_os_version, ' \
                'lv.config_browser_engine, lv.config_browser_name, ' \
                'lv.config_browser_version, lv.config_resolution ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'WHERE lv.idvisitor = UNHEX(\''+visitorid+'\') ' \

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)
        cur.execute(query)

        # fetch all of the rows from the query
        data = cur.fetchall()

        visitor_dict = {
            "firstVisit": None,
            "lastVisit": None
        }
        geo_locations_dict = {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None
        }
        devices_dict = {
            "name": None,
            "description": None,
            "type": None,
            "operatingSystem": None,
            "browser": None,
            "resolution": None
        }
        devices_list = []
        geo_locations_list = []

        if len(data) > 0:

            visitor_dict = {
                "firstVisit": str(data[0][0]),
                "lastVisit": str(data[-1][1]),
            }
            for row in data:
                geo_locations_dict = {
                    "country": str(row[2]),
                    "city": str(row[3]),
                    "latitude": str(row[4]),
                    "longitude": str(row[5])
                }
                geo_locations_list.append(geo_locations_dict)

                description = None
                name = None
                type = None

                if row[6]:
                    name = str(row[6])
                    description = str(row[6])
                if row[7] and row[6]: description = str(row[6])+', '+str(row[7])
                if row[8]: type = str(row[8])

                devices_dict = {
                    "name": name,
                    "description": description,
                    "type": type,
                    "operating_system": str(row[9])+', '+str(row[10]),
                    "browser": str(row[11])+', '+str(row[12])+', '+str(row[13]),
                    "resolution": str(row[14]),
                }
                devices_list.append(devices_dict)

        visitor_dict['geoLocation'] = geo_locations_list
        visitor_dict['device'] = devices_list

        cur.close()
        cnx.close()

        return visitor_dict

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'siteid': siteid, 'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'id': siteid, 'value': 'Error'}
        raise e


def get_matomo_visitor_tracking_data(visitorid):
    '''
    :param visitorid: id of visitor which data will be returned
    :return: dictionary with visitor tracking data
    '''
    try:
        query = 'SELECT lv.visitor_returning, ' \
                'inet_ntoa(conv(hex(location_ip), 16, 10)) AS location_ip, ' \
                'lv.visitor_count_visits, lv.visit_last_action_time, ' \
                'lv.visit_first_action_time, lv.visit_goal_converted, ' \
                'lv.visitor_days_since_first, lv.visitor_days_since_order, ' \
                'lv.visit_total_searches, lv.visit_total_actions, ' \
                'lv.visit_total_interactions, lv.visitor_returning, ' \
                'lv.idsite, lv.visit_total_time, lc.revenue, lc.server_time, ' \
                'lci.price, lci.quantity, lci.deleted ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_conversion` lc ' \
                'ON lv.idvisit = lc.idvisit ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_conversion_item` lci ' \
                'ON lv.idvisit = lci.idvisit ' \
                'WHERE lv.idvisitor = UNHEX(\''+visitorid+'\') ' \
                'ORDER BY lv.idvisit '

        page_query = 'SELECT lva.idaction_url, la.name ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_link_visit_action` lva ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la ' \
                'ON lva.idaction_url = la.idaction ' \
                'WHERE lva.idvisit IN (SELECT lv.idvisit ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'WHERE lv.idvisitor = UNHEX(\''+visitorid+'\') )' \

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        cur.execute(page_query)
        page_view_data = cur.fetchall()

        unique_page_view_set = set()
        revisited_pages_set = set()

        for page_view in page_view_data:
            if page_view[1] in unique_page_view_set:
                revisited_pages_set.add(page_view[1])
            unique_page_view_set.add(page_view[1])

        total_page_views = len(page_view_data)
        total_unique_page_view = len(unique_page_view_set)
        total_revisited_pages = len(revisited_pages_set)

        return_dict = {
            "hasMoreVisits": None,
            "ipAddress": None,
            "totalVisits": None,
            "totalPageViews": None,
            "totalUniquePageViews": None,
            "totalRevisitedPages": None,
            "totalEcommerceRevenue": None,
            "totalEcommerceConversions": None,
            "totalEcommerceItems": None,
            "totalAbandonedCarts": None,
            "totalAbandonedCartsRevenue": None,
            "totalVisitorDuration": None,
            "serverDate": None,
            "lastActionTimestamp": None,
            "firstActionTimestamp": None,
            "visitConverted": None,
            "daysSinceFirstVisit": None,
            "daysSinceLastEcommerceOrder": None,
            "searches": None,
            "actions": None,
            "interactions": None
        }

        cur.execute(query)
        data = cur.fetchall()

        if(len(data)>0):

            total_ecommerce_revenue = 0
            total_abandoned_carts_revenue = 0
            total_ecommerce_items = 0
            total_ecommerces = 0
            total_abandoned_carts = 0
            total_visits = 0
            total_visitor_duration = 0
            total_ecommerce_conversions = 0

            for row in data:
                if(row[14]): # total_ecommerce_revenue & total_abandoned_carts_revenue
                    if(row[18] == 0):
                        total_ecommerce_revenue += int(row[14])
                    else:
                        total_abandoned_carts_revenue += int(row[14])

                if(row[17]):
                    if(row[14] == 0): # total_ecommerce_items
                        total_ecommerce_items += int(row[17])
                        total_ecommerces += 1
                    else:
                        total_abandoned_carts += 1

                if(row[2]): # total_visits
                    total_visits += int(row[2])

                if(row[13]): # total_visitor_duration
                    total_visitor_duration += int(row[13])

            if(total_ecommerces>0): total_ecommerce_conversions = total_visits / total_ecommerces

            return_dict = {
                "hasMoreVisits": str(data[0][0]),
                "ipAddress": str(data[0][1]),
                "totalVisits": str(data[0][2]),
                "totalPageViews": str(total_page_views),
                "totalUniquePageViews": str(total_unique_page_view),
                "totalRevisitedPages": str(total_revisited_pages),
                "totalEcommerceRevenue": str(total_ecommerce_revenue),
                "totalEcommerceConversions": str(total_ecommerce_conversions),
                "totalEcommerceItems": str(total_ecommerce_items),
                "totalAbandonedCarts": str(total_abandoned_carts),
                "totalAbandonedCartsRevenue": str(total_abandoned_carts_revenue),
                "totalVisitorDuration": str(total_visitor_duration),
                "serverDate": str(data[0][15]),
                "lastActionTimestamp": str(data[-1][3]),
                "firstActionTimestamp": str(data[0][4]),
                "visitConverted": str(data[0][5]),
                "daysSinceFirstVisit": str(data[0][6]),
                "daysSinceLastEcommerceOrder": str(data[0][7]),
                "searches": str(data[0][8]),
                "actions": str(data[0][9]),
                "interactions": str(data[0][10])
            }

        return return_dict

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'siteid': siteid, 'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'id': siteid, 'value': 'Error'}
        raise e


def get_matomo_site(siteid):
    '''
    :param siteid: id of site which data will be returned
    :return: dictionary of site data
    '''
    try:

        query = 'SELECT si.name, si.main_url, si.ts_created, si.ecommerce ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`site` si ' \
                'WHERE si.idsite=' + str(siteid) + ';'

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)
        cur.execute(query)

        # fetch all of the rows from the query
        data = cur.fetchall()

        value = {
            'idSite': siteid,
            'name': None,
            'mainUrl': None,
            'tsCreated': None,
            'ecommerce': None
        }

        if len(data) > 0:
            for row in data:
                value = {
                    'idSite': siteid,
                    'name': str(row[0]) ,
                    'mainUrl':  str(row[1]) ,
                    'tsCreated':  str(row[2]) ,
                    'ecommerce':  str(row[3])
                }
        cur.close()
        cnx.close()

        return value

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'siteid': siteid, 'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'id': siteid, 'value': 'Error'}
        raise e


def number_of_visits(token_auth, time_from, time_to):
    '''
    :param token_auth: superuser's token
    :param time_from: start time for interval
    :param time_to: stop time for interval
    :return: list of sites and their visits & unique visits
    '''

    try:
        query = 'SELECT superuser_access ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`user` ' \
                'WHERE token_auth=\''+token_auth+'\' '

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)
        cur.execute(query)

        # fetch all of the rows from the query
        superuser_access = cur.fetchall()[0][0]

        if superuser_access == 1:

            query = 'SELECT lv.idsite, si.name, COUNT(DISTINCT lv.idvisitor), COUNT(lv.idvisitor) ' \
                    'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                    'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`site` si ' \
                    'ON lv.idsite = si.idsite ' \
                    'WHERE DATE(lv.visit_last_action_time) BETWEEN \''+str(time_from)+'\' AND \''+str(time_to)+'\'' \
                    'GROUP BY idsite'


            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(buffered=True)
            cur.execute(query)

            # fetch all of the rows from the query
            site_data = cur.fetchall()

            site_list = []
            for site in site_data:
                site_dict = {
                    'siteId': str(site[0]),
                    'siteName': str(site[1]),
                    'visits': str(site[3]),
                    'uniqueVisits': str(site[2])
                }
                site_list.append(site_dict)
            return_dict = {
                'fromTime': str(time_from),
                'toTime': str(time_to),
                'sitesFound': len(site_data),
                'sites': site_list
            }

            return return_dict

        else:
            raise e401

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'value': 'Error'}
        raise e


def get_visitor_journey(visit_tracking_id):
    print('JOURNEY')
    if not visit_tracking_id:
        return None

    # "id": "journey_id_iwuerieuieur",
    # "timestamp": "38409",
    # "visitEntryUrl": "https://www.sme.sk",
    # "visitExitUrl": "https://www.sme.sk/politics",
    # "interactionPosition": "1",
    # "timeSpent": "22"

    query = 'SELECT lva.idlink_va, lva.idvisit, lva.server_time, la.name, la_ref.name, '\
            'lva.interaction_position, lva.time_spent ' \
            'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_link_visit_action` lva ' \
            'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la ' \
            'ON la.idaction = lva.idaction_url ' \
            'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_ref ' \
            'ON la_ref.idaction = lva.idaction_url_ref ' \
            'WHERE idvisit = '+str(visit_tracking_id)+' ' \
            'ORDER BY lva.interaction_position '

    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor(buffered=True)
    cur.execute(query)
    journeys = cur.fetchall()

    if not journeys:
        return None

    return journeys


def partner_number_of_visits(token_auth, partner_id, time_from, time_to):
    '''
    :param token_auth: user's autentication token
    :param partner_id: id of partner which site's data will be returned
    :param time_from: start time of interval
    :param time_to: stop time of interval
    :return: a list of partners sites and their visits & unique visits
    '''

    try:
        query = 'SELECT lv.idsite, si.name, COUNT(DISTINCT lv.idvisitor), COUNT(lv.idvisitor) ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`site` si ' \
                'ON lv.idsite = si.idsite ' \
                'WHERE DATE(lv.visit_last_action_time) BETWEEN \''+str(time_from)+'\' AND \''+str(time_to)+'\' ' \
                'AND lv.idsite IN (SELECT DISTINCT ac.idsite ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`access` ac ' \
                'WHERE (ac.access=\'admin\' OR ac.access=\'view\') AND ac.login IN (SELECT login ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`user` ' \
                'WHERE token_auth=\''+token_auth+'\') ) ' \
                'GROUP BY idsite '


        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)
        cur.execute(query)

        # fetch all of the rows from the query
        site_list = cur.fetchall()

        if site_list:
            site_visitors_list = []
            for site in site_list:
                site_dict = {
                    'siteId': str(site[0]),
                    'siteName': str(site[1]),
                    'visits': str(site[3]),
                    'uniqueVisits': str(site[2])
                }
                site_visitors_list.append(site_dict)

            return_dict = {
            'fromTime': str(time_from),
            'toTime': str(time_to),
            'sitesFound': len(site_list),
            'sites': site_visitors_list
            }

            return return_dict

        else:
            e404.data = {'message': 'authorization token {} does not have access to any sites'.format(token_auth)}
            raise e404

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'value': 'Error'}
        raise e


def get_matomo_visitor_statistics(token_auth, visitor_id, from_date, to_date):

    try:
        visitQuery = 'SELECT lv.idsite, ' \
                'inet_ntoa(conv(hex(location_ip), 16, 10)) AS location_ip, ' \
                'lv.visit_goal_converted, lv.visit_first_action_time, ' \
                'lv.visit_last_action_time, lv.visitor_returning, ' \
                'lv.visitor_count_visits, lv.visitor_days_since_first, ' \
                'lv.visitor_days_since_order, lv.visit_total_time, ' \
                'lv.visit_total_searches, lv.visit_total_actions, ' \
                'lv.visit_total_interactions, lv.referer_type, lv.referer_name, ' \
                'lv.referer_url, lv.location_browser_lang, ' \
                'lv.config_device_type, lv.config_device_brand, ' \
                'lv.config_device_model, lv.config_os, lv.config_os_version, ' \
                'lv.config_browser_name, lv.config_browser_version, ' \
                'lv.config_browser_engine, lv.visit_total_events, ' \
                'lv.location_country, lv.location_region, lv.location_city, ' \
                'lv.location_latitude, lv.location_longitude, ' \
                'lv.visitor_localtime, lv.visitor_days_since_last, ' \
                'lv.custom_var_k1, lv.custom_var_v1, ' \
                'lv.config_resolution, lv.location_provider, ' \
                'lv.location_hostname, lv.idvisit, st.name ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`site` st ' \
                'ON lv.idsite = st.idsite ' \
                'WHERE lv.idvisitor = UNHEX(\''+str(visitor_id)+'\') '  \
                'AND DATE(lv.visit_last_action_time) BETWEEN \''+str(from_date)+'\' AND \''+str(to_date)+'\' ' \
                'AND lv.idsite IN (SELECT idsite FROM ' \
                '`' + app.config.MATOMO_DATABASE_NAME + '`.`access` da, ' \
                '`' + app.config.MATOMO_DATABASE_NAME + '`.`user` du ' \
                'WHERE da.login = du.login ' \
                'AND du.token_auth=\''+token_auth+'\') '

        actionQuery = 'SELECT lva.idvisit, lva.idpageview, ' \
                 'lva.server_time, lva.time_spent, ' \
                 'lva.interaction_position, lva.bandwidth, ' \
                 'la_name.name, la_name.type, la_url.name, ' \
                 'la_url.type, lv.referer_keyword, lv.referer_type ' \
                 'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_link_visit_action` lva ' \
                 'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_name ' \
                 'ON lva.idaction_name = la_name.idaction ' \
                 'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_url ' \
                 'ON lva.idaction_url = la_url.idaction ' \
                 'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                 'ON lva.idvisit = lv.idvisit ' \
                 'WHERE lva.idvisit IN (SELECT lv.idvisit ' \
                 'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                 'WHERE lv.idvisitor = UNHEX(\''+str(visitor_id)+'\') ' \
                 'AND DATE(lv.visit_last_action_time) BETWEEN \'' + str(from_date) + '\' AND \'' + str(to_date) + '\' ) '

        ecommerceQuery = 'SELECT lci.idvisit, lci.idorder, ' \
                'lc.revenue, lc.revenue_subtotal, lc.revenue_tax, ' \
                'lc.revenue_shipping, lc.revenue_discount, lc.items, ' \
                'lci.server_time, lci.price, lci.quantity, lci.deleted, ' \
                'la_sku.name, la_name.name, la_name.type ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_conversion_item` lci ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_sku ' \
                'ON lci.idaction_sku = la_sku.idaction ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_name ' \
                'ON lci.idaction_name = la_name.idaction ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_conversion` lc ' \
                'ON lci.idvisit = lc.idvisit AND lci.idorder = lc.idorder ' \
                'WHERE lci.idvisit IN (SELECT lv.idvisit ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'WHERE lv.idvisitor = UNHEX(\''+str(visitor_id)+'\') ' \
                'AND DATE(lv.visit_last_action_time) BETWEEN \'' + str(from_date) + '\' AND \'' + str(to_date) + '\' ) '


        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        # queries
        cur.execute(visitQuery)
        visit_data = cur.fetchall()
        cur.execute(ecommerceQuery)
        ecommerce_data = cur.fetchall()
        cur.execute(actionQuery)
        action_data = cur.fetchall()

        cur.close()
        cnx.close()

        return visit_data, ecommerce_data, action_data

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        raise e
