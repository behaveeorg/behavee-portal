from app import db
import app.config
import mysql.connector
from werkzeug.exceptions import BadRequest
import datetime as dt
from datetime import timedelta
import time
import os

from sqlalchemy import exc
from app.models.behavee import *
from app.constants import media_types, PARTNER_TYPE, DEVICE_TYPE, LANGUAGES, VISITOR_TYPE, GEO_LOCATION_TYPE, \
    CONTENT_TYPE, MEDIA_TYPE, CONTACT_TYPE, SITE_TYPE, CURRENCY, PRODUCT_TRACKING_TYPE
from .toolbox import most_common, check_type, check_if_exist, post_type, get_type


config = {
    'user': app.config.MATOMO_DATABASE_USER,
    'password': app.config.MATOMO_DATABASE_PASS,
    'host': app.config.MATOMO_DATABASE_HOST,
    'port': app.config.MATOMO_DATABASE_PORT,
    'database': app.config.MATOMO_DATABASE_NAME,
    'connection_timeout': 3600,
}


class Log:
    def __init__(self, mode, timestamp, current_time):
        self.file = open('./log/'+str(mode)+'_log.txt', 'a+')
        self.file.write('==========================\n')
        self.file.write(' '+str(mode).capitalize()+' Synchonization \n')
        self.file.write(' FROM: '+str(timestamp.strftime("%Y-%m-%d %H:%M:%S"))+' \n')
        self.file.write('   TO: '+str(current_time.strftime("%Y-%m-%d %H:%M:%S"))+' \n')
        self.file.write('===========================\n')

    def add(self, text):
        self.file.write(str(text)+'\n')

    def save(self):
        self.file.write('\n\n')
        self.file.close()


def sync_manager(token_auth, sync_id, arg1, arg2, arg3):
    try:
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        # query matomo database with token_auth and return user login
        query = 'SELECT du.login FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`user` du '\
                'WHERE du.token_auth=\'' + token_auth + '\' AND du.superuser_access = 1 '

        cur.execute(query)
        login = cur.fetchall()

        # if user login exist then given token_auth is in database
        if len(login) > 0:

            if sync_id is None:
                return "imput valid sync_id"

            if sync_id == 0:
                return sync_user()

            if sync_id == 1:
                return sync_sites()

            if sync_id == 2:
                return sync_product_sales(arg1)

            if sync_id == 3:
                return sync_product_tracking_record(arg1, arg2, arg3)

            if sync_id == 4:
                return sync_visitor_tracking_record(arg1, arg2, arg3)

            if sync_id == 5:
                return sync_product_skus_attributes()

            if sync_id == 6:
                return sync_products_attributes()

            if sync_id == 7:
                return sync_visitors_table()

            if sync_id == 8:
                return get_matomo_tracking_site_ids()

            if sync_id == 9:
                return sync_site(arg1)

            if sync_id == 10:
                return create_synchronizer(arg1)

            if sync_id == 11:
                return delete_synchronizer(arg1)

            if sync_id == 12:
                return add_site_partner(arg1, arg2)

            return "Unauthorized request - you need to imput superuser's authorization token"

        else:
            pass

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'value': 'error'}
        raise e


def get_matomo_tracking_site_ids():
    '''
    :return: a list of all sites from matomo
    '''
    try:
        query = 'SELECT idsite ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`site` '

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        cur.execute(query)
        data = cur.fetchall()

        if not data:
            return 'no sites found'

        site_list = []
        for site in data:
            site_list.append(site[0])

        return_dict = {
            'sites': site_list
        }
        return return_dict

    except:
        return 'something went wrong'


def sync_products_attributes():
    '''
    synchronizes attributes from product sku to core products
    attributes:
        no of purchases
        no of refusals
        first purchase
        last purchase
    '''
    limit = 2500
    offset = 0
    while True:
        products = db.session.query(Product)\
            .join(ProductSku)\
            .limit(limit).offset(offset).all()

        if not products:
            return 'products attributes synchronization done'

        for product in products:
            if product.product_sku:
                prices = []
                refusals = 0
                purchases = 0
                for sku in product.product_sku:
                    if sku.price: prices.append(sku.price)
                    if sku.no_of_refusals: refusals += sku.no_of_refusals
                    if sku.no_of_purchases: purchases += sku.no_of_purchases

                if sku.last_purchase and product.last_purchase:
                    if sku.last_purchase > product.last_purchase:
                        product.last_purchase = sku.last_purchase
                elif sku.last_purchase:
                    product.last_purchase = sku.last_purchase

                if sku.first_purchase and product.first_purchase:
                    if sku.first_purchase < product.first_purchase:
                        product.first_purchase = sku.first_purchase
                elif sku.first_purchase:
                    product.first_purchase = sku.first_purchase

                product.no_of_refusals = refusals
                product.no_of_purchases = purchases

                if len(prices) < 1:
                    continue

                product.average_price = round(sum(prices) / int(len(prices)),2)
                product.lowest_price = min(prices)
                product.highest_price = max(prices)

        db.session.commit()
        offset += limit


def sync_product_skus_attributes():
    '''
    synchronizes attributes from product tracking record to product skus
    attributes:
        no of purchases
        no of refusals
        first purchase
        last purchase
    '''
    limit = 2500
    offset = 0
    while True:
        product_skus = db.session.query(ProductSku)\
            .join(ProductTrackingRecord)\
            .limit(limit).offset(offset).all()

        if not product_skus:
            return 'product skus attributes synchronization done'

        for sku in product_skus:
            if sku.product_tracking_record:
                refusals = 0
                purchases = 0

                for tracking_record in sku.product_tracking_record:

                    if tracking_record.type:
                        if tracking_record.type == 1:
                            purchases += 1
                        elif tracking_record.type == 2 or \
                            tracking_record.type == 3 or \
                            tracking_record.type == 4:
                            refusals += 1

                    if tracking_record.timestamp and sku.last_purchase:
                        if tracking_record.timestamp > sku.last_purchase:
                            sku.last_purchase = tracking_record.timestamp
                    elif tracking_record.timestamp:
                        sku.last_purchase = tracking_record.timestamp

                    if tracking_record.timestamp and sku.first_purchase:
                        if tracking_record.timestamp < sku.first_purchase:
                            sku.first_purchase = tracking_record.timestamp
                    elif tracking_record.timestamp:
                        sku.first_purchase = tracking_record.timestamp

                sku.no_of_refusals = refusals
                sku.no_of_purchases = purchases

        db.session.commit()
        offset += limit


def sync_visitors_table():
    '''
    function that query visitor tracking records and create a new instance of visitor
    for every new visitor in visitor tracking record
    '''
    sites = db.session.query(BehaveeSite).all()

    if not sites:
        return 'no sites in database'

    site_dict = {
        0: None
    }
    for site in sites:
        site_dict[str(site.id)] = site.partner_id

    limit = 10000

    start_time = time.time()

    i = 0
    while True:
        start_time = time.time()
        new_visitors = db.session.query(VisitorTrackingRecord.visitor_tracking_id, VisitorTrackingRecord.site_id)\
            .outerjoin(Visitor, Visitor.visitor_tracking_id == VisitorTrackingRecord.visitor_tracking_id) \
            .filter(Visitor.visitor_tracking_id == None) \
            .limit(limit).distinct().all()


        if len(new_visitors) < 1:
            break

        commit_list = []
        for visitor in new_visitors:
            commit_list.append(Visitor(
                visitor_tracking_id = visitor[0],
                partner_id = check_if_exist(site_dict, str(visitor[1]))
            ))
        db.session.bulk_save_objects(commit_list)
        db.session.commit()

        i += 1
        continue

    return 0


def sync_visitor_attributes(visitor_id):
    '''
    :param visitor_id: id of visitor to synchronize
    synchronizes all attributes from visitor tracking record to visitor table for given visitor id
    '''

    visitor = db.session.query(Visitor)\
        .filter(Visitor.id == visitor_id).first()

    if not visitor:
        return None

    trackings = db.session.query(VisitorTrackingRecord)\
        .filter(VisitorTrackingRecord.visitor_tracking_id == visitor.visitor_tracking_id).all()

    if not trackings:
        return None

    # list of id of visits that were ecommerce
    visit_tracking_ecommerce = list(tracking.visit_tracking_id for tracking in trackings if tracking.visit_goal_buyer != 0)

    ecommerce_tracking = db.session.query(ProductTrackingRecord)\
        .filter(ProductTrackingRecord.visit_tracking_id.in_(visit_tracking_ecommerce)).all()

    total_purchase = len(list(tracking for tracking in ecommerce_tracking if tracking.type == 1))
    total_refusals = len(list(tracking for tracking in ecommerce_tracking if tracking.type == 2 \
                              or tracking.type == 3 or tracking.type == 4))
    purchased_id = list(tracking.product_sku_id for tracking in ecommerce_tracking if tracking.type == 1)
    refused_id = list(tracking.product_sku_id for tracking in ecommerce_tracking if tracking.type == 2 \
                      or tracking.type == 3 or tracking.type == 4)
    total_revenue = sum(list(tracking.price for tracking in ecommerce_tracking if tracking.type == 1))
    total_refused_revenue = sum(list(tracking.price for tracking in ecommerce_tracking if tracking.type == 2))
    total_potential_revenue = sum(list(tracking.price for tracking in ecommerce_tracking if tracking.type == 3 \
                                       or tracking.type == 4))
    converted = max(list(tracking.visit_goal_converted for tracking in trackings))

    if len(trackings) > 1: has_more_visits = 1
    else: has_more_visits = 0
    if len(ecommerce_tracking) > 0:
        last_purchase = None
        timestamp = datetime(1990, 1, 1, 00, 00, 00)
        for i,tracking in enumerate(ecommerce_tracking):
            if tracking.type == 1:
                if tracking.timestamp:
                    if tracking.timestamp > timestamp:
                        last_purchase = tracking.timestamp
                        timestamp = tracking.timestamp

    else: last_purchase = None
    if has_more_visits >= 1:
        visitor_type = 'returning'
    else:
        visitor_type = 'new'

    if not visitor:
        visitor = Visitor(
        visitor_tracking_id = visitor_id,
        first_visit = trackings[0].from_timestamp,
        last_visit = trackings[-1].from_timestamp,
        has_more_visits = has_more_visits,
        total_visits = len(trackings),
        total_visit_duration = sum(list(visit.visit_total_time for visit in trackings)),
        total_actions = sum(list(visit.visitor_journey_count for visit in trackings)),
        total_outlinks = None,
        total_downloads = None,
        total_searches = None,
        total_page_views = None,
        total_unique_page_views = None,
        total_revisited_pages = None,
        total_page_views_with_timing = None,
        total_product_purchases = total_purchase,
        total_product_refusals = total_refusals,
        total_product_views = None,
        total_product_searches = None,
        most_visited_site_name = None,
        most_purchased_product_sku_id = most_common(purchased_id),
        most_refused_product_sku_id = most_common(refused_id),
        most_viewed_product_sku_id = None,
        most_searched_product_sku_id = None,
        last_purchase = last_purchase,
        targeted = None,
        converted = converted,
        total_revenue = total_revenue,
        total_refused_revenue = total_refused_revenue,
        total_potential_revenue = total_potential_revenue,
        deleted = False,
        visitor_type = post_type(VISITOR_TYPE, visitor_type)
        )
        db.session.add(visitor)
        db.session.commit()
        return visitor

    visitor.first_visit = trackings[0].from_timestamp
    visitor.last_visit = trackings[-1].from_timestamp
    visitor.has_more_visits = has_more_visits
    visitor.total_visits = len(trackings)
    visitor.total_visit_duration = sum(list(visit.visit_total_time for visit in trackings))
    visitor.total_actions = sum(list(visit.visitor_journey_count for visit in trackings))
    visitor.total_outlinks = None
    visitor.total_downloads = None
    visitor.total_searches = None
    visitor.total_page_views = None
    visitor.total_unique_page_views = None
    visitor.total_revisited_pages = None
    visitor.total_page_views_with_timing = None
    visitor.total_product_purchases = total_purchase
    visitor.total_product_refusals = total_refusals
    visitor.total_product_views = None
    visitor.total_product_searches = None
    visitor.most_visited_site_name = None
    visitor.most_purchased_product_sku_id = most_common(purchased_id)
    visitor.most_refused_product_sku_id = most_common(refused_id)
    visitor.most_viewed_product_sku_id = None
    visitor.most_searched_product_sku_id = None
    visitor.last_purchase = last_purchase
    visitor.targeted = None
    visitor.converted = converted
    visitor.total_revenue = total_revenue
    visitor.total_refused_revenue = total_refused_revenue
    visitor.total_potential_revenue = total_potential_revenue
    visitor.visitor_type = post_type(VISITOR_TYPE, visitor_type)
    db.session.commit()
    return visitor


def sync_product_sales(sync_id):

    try:
        sync = db.session.query(BehaveeSynchronizer)\
            .filter(BehaveeSynchronizer.id == sync_id).first()

        if not sync:
            e404.data = {'message': 'synchronizer with id {} not found'.format(sync_id)}
            raise e404

        if sync.last_product_sales_synchronization >= datetime.date(sync.last_product_synchronization):
            return 'synchronization done to date of last product synchronization'

        sync_date = sync.last_product_sales_synchronization + timedelta(days=1)

        query = '(SELECT DATE(timestamp), site_id, product_sku, product_sku_name, '\
                'SUM(quantity)*price, SUM(quantity), type, product_sku_id ' \
                'FROM product_tracking_record ' \
                'WHERE type = 1 AND DATE(timestamp) = \''+str(sync_date)+'\' ' \
                'GROUP BY product_sku ' \
                'ORDER BY COUNT(product_sku) DESC ' \
                'LIMIT 3) ' \
                'UNION ' \
                '(SELECT DATE(timestamp), site_id, product_sku, product_sku_name, ' \
                'SUM(quantity)*price, SUM(quantity), type, product_sku_id ' \
                'FROM product_tracking_record ' \
                'WHERE type = 2 AND DATE(timestamp) = \''+str(sync_date)+'\' ' \
                'GROUP BY product_sku ' \
                'ORDER BY COUNT(product_sku) DESC ' \
                'LIMIT 3) ' \
                'UNION ' \
                '(SELECT DATE(timestamp), site_id, product_sku, product_sku_name, ' \
                'SUM(quantity)*price, SUM(quantity), type, product_sku_id ' \
                'FROM product_tracking_record ' \
                'WHERE type = 3 AND DATE(timestamp) = \''+str(sync_date)+'\' ' \
                'GROUP BY product_sku ' \
                'ORDER BY COUNT(product_sku) DESC ' \
                'LIMIT 3) ' \
                'UNION ' \
                '(SELECT DATE(timestamp), site_id, product_sku, product_sku_name, ' \
                'SUM(quantity)*price, SUM(quantity), type, product_sku_id ' \
                'FROM product_tracking_record ' \
                'WHERE type = 4 AND DATE(timestamp) = \''+str(sync_date)+'\' ' \
                'GROUP BY product_sku ' \
                'ORDER BY COUNT(product_sku) DESC ' \
                'LIMIT 3) '

        data = db.session.execute(query).fetchall()

        if not data:
            sync.last_product_sales_synchronization = sync_date
            db.session.commit()
            return 0

        commit_list = []
        last_type = -1
        for row in data:
            if str(row[6]) != str(last_type):
                i = 0
                last_type = str(row[6])
            i += 1
            commit_list.append(ProductSales(
                site_id = row[1],
                timestamp = row[0],
                product_sku = row[2],
                product_sku_name = row[3],
                value = row[4],
                quantity = row[5],
                type = row[6],
                product_sku_id = row[7],
                position = i
            ))

        sync.last_product_sales_synchronization = sync_date
        db.session.bulk_save_objects(commit_list)
        db.session.commit()

    except:
        return 'error'

    return 0


def sync_user():
    '''
    function that synchronizes user's data from matomo to backend db
    '''

    behavee_synchronizer = db.session.query(BehaveeSynchronizer) \
        .filter(BehaveeSynchronizer.id == 1).first()

    current_time = dt.datetime.now()

    if not behavee_synchronizer:
        return 'could not load last synchronization timestamp'

    last_sync = behavee_synchronizer.last_user_synchronization
    behavee_synchronizer.last_user_synchronization = dt.datetime.now()

    query = 'SELECT login, email, token_auth, superuser_access ' \
        'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`user` ' \
        'WHERE date_registered BETWEEN \'' + str(last_sync) + '\' ' \
        'AND \'' + str(current_time) + '\''

    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor(buffered=True)

    cur.execute(query)
    data = cur.fetchall()

    commit_list = []
    if data:
        for user in data:
            behavee_user = db.session.query(BehaveeUser)\
                .filter(BehaveeUser.login == user[0])\
                .filter(BehaveeUser.token_auth == user[2]).all()

            if behavee_user:
                continue

            contact = Contact(
                email=user[1]
            )
            behavee_user = BehaveeUser(
                login=user[0],
                token_auth=user[2],
                superuser=user[3]
            )
            behavee_user.contact.append(contact)
            commit_list.append(behavee_user)

    db.session.add_all(commit_list)
    db.session.commit()
    return 'user synchronization done'


def sync_sites():
    '''
    function that synchronizes sites data from matomo to backend db
    '''

    try:
        behavee_synchronizer = db.session.query(BehaveeSynchronizer).first()

        if not behavee_synchronizer:
            return 'could not load last synchronization timestamp'

        last_sync = behavee_synchronizer.last_site_synchronization
        current_time = dt.datetime.now()
        behavee_synchronizer.last_site_synchronization = dt.datetime.now()

        query = 'SELECT idsite, name, main_url ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`site` ' \
                'WHERE ts_created BETWEEN \''+str(last_sync)+'\' ' \
                'AND \'' + str(current_time) + '\''

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        cur.execute(query)
        data = cur.fetchall()

        if data:
            for site in data:
                behavee_site = BehaveeSite(
                                tracking_site_id = site[0],
                                site_name = site[1],
                                url = site[2])
                db.session.add(behavee_site)

        db.session.commit()

        sites = db.session.query(BehaveeSite).all()

        if not sites:
            return 'no sites in db'

        for site in sites:

            visit_query = 'SELECT AVG(lv.visit_total_time), COUNT(lv.idvisit) ' \
                          'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                          'WHERE lv.idsite=' + str(site.tracking_site_id) + ' ' \
                          'AND (lv.visit_last_action_time BETWEEN \'' + str(last_sync) + '\' '\
                          'AND \'' + str(current_time) + '\' )' \

            date_query = '(SELECT visit_first_action_time ' \
                         'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                         'WHERE lv.idsite=' + str(site.tracking_site_id) + ' ' \
                         'AND (lv.visit_last_action_time BETWEEN \'' + str(last_sync) + '\' '\
                         'AND \'' + str(current_time) + '\' )' \
                         'ORDER BY idvisit DESC ' \
                         'LIMIT 1 ) UNION ALL ' \
                         '(SELECT visit_first_action_time ' \
                         'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                         'WHERE lv.idsite=' + str(site.tracking_site_id) + ' ' \
                         'AND (lv.visit_last_action_time BETWEEN \'' + str(last_sync) + '\' '\
                         'AND \'' + str(current_time) + '\' )' \
                         'ORDER BY idvisit ASC LIMIT 1 )'

            cur.execute(visit_query)
            visit = cur.fetchall()
            cur.execute(date_query)
            date = cur.fetchall()

            if len(date) < 1 and visit[0][1] < 1:
                continue

            if len(visit) > 0:
                if site.no_of_views and site.average_time_spent:
                    avg = ((site.no_of_views * site.average_time_spent) + (visit[0][1] * visit[0][0])) / (
                            site.no_of_views + visit[0][1])
                    site.no_of_views = site.no_of_views + visit[0][1]
                    site.average_time_spent = avg
                else:
                    site.no_of_views = visit[0][1]
                    site.average_time_spent = visit[0][0]

            if len(date)>0:
                if site.first_view:
                    if date[1][0] < site.first_view: site.first_view = date[1][0]
                else:
                    site.first_view = date[1][0]
                if site.last_view:
                    if date[0][0] > site.last_view: site.last_view = date[0][0]
                else:
                    site.last_view = date[0][0]

            db.session.flush()

        db.session.commit()
        return 'site synchronization done'

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


def sync_site(site_id):
    '''
    :param site_id: tracking_site_id (matomo site id) to synchronize site from matomo to backend
    synchronizes given site id from matomo to backend db
    '''

    try:
        site = db.session.query(BehaveeSite)\
            .filter(BehaveeSite.tracking_site_id == site_id).first()

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)
        if not site:

            query = 'SELECT name, main_url ' \
                    'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`site` ' \
                    'WHERE idsite = \''+str(site_id)+'\' '

            cur.execute(query)
            data = cur.fetchall()

            if not data:
                return 'could not find site id '+str(site_id)

            site = BehaveeSite(
                site_name=data[0][0],
                url=data[0][1],
                tracking_site_id=site_id
            )
            db.session.add(site)
            db.session.commit()

        visit_query = 'SELECT AVG(lv.visit_total_time), COUNT(lv.idvisit) ' \
                      'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                      'WHERE lv.idsite=' + str(site_id) + ' '

        date_query = '(SELECT visit_first_action_time ' \
                     'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                     'WHERE lv.idsite=' + str(site_id) + ' ' \
                     'ORDER BY idvisit DESC ' \
                     'LIMIT 1 ) UNION ALL ' \
                     '(SELECT visit_first_action_time ' \
                     'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                     'WHERE lv.idsite=' + str(site_id) + ' ' \
                     'ORDER BY idvisit ASC LIMIT 1 )'

        cur.execute(visit_query)
        visit = cur.fetchall()
        cur.execute(date_query)
        date = cur.fetchall()

        if len(date) < 1 and visit[0][1] < 1:
            return 0

        if len(visit) > 0:
            site.no_of_views = visit[0][1]
            site.average_time_spent = visit[0][0]

        if len(date)>0:
            site.first_view = date[1][0]
            site.last_view = date[0][0]


        db.session.commit()
        return 0

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


def sync_partner():
    '''
    UNUSED
    function that synchronizes partner data from matomo to backend
    '''
    return 'partner synchronization does not work yet'


def sync_product_tracking_record(days, site_id, sync_id):
    '''
    :param days: how many days synchronizes in one function call
    :param site_id: site id which products ecommerce should be synchronized
    :param sync_id: behavee synchronizer id - to read last sync timestamp, and save current sync timestamp
    synchronizes products ecommerce from matomo to backend db for given site and number of days
    '''

    try:
        if not days:
            return 'add arg1 - days'

        if not site_id:
            return 'add arg2 - site id'

        if not sync_id:
            return 'add arg3 - sync id'

        if int(days) > 7:
            return 'cant synchronize more then 7 days at once'

        start_time = time.time()
        behavee_synchronizer = db.session.query(BehaveeSynchronizer) \
            .filter(BehaveeSynchronizer.id == sync_id).first()

        if not behavee_synchronizer:
            return 'could not load last time synchronization'

        last_sync = behavee_synchronizer.last_product_synchronization

        try: current_time = last_sync + timedelta(days=int(days))
        except:
            return 'arg1 is not inteeger'

        now = dt.datetime.now()

        if (last_sync + timedelta(minutes=1)) > now:
            return 'synchronization done to current time'

        if now < current_time:
            current_time = now

        query = 'SELECT la_name.name, la_sku.name, lci.price, lci.quantity, lci.server_time, '\
                'lci.idorder, lci.deleted, HEX(lci.idvisitor), lci.idvisit, lci.quantity, lci.idsite ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_conversion_item` lci ' \
                'JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_name ' \
                'ON lci.idaction_name = la_name.idaction ' \
                'JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_sku ' \
                'ON lci.idaction_sku = la_sku.idaction ' \
                'WHERE idsite = '+str(site_id)+' AND lci.server_time BETWEEN ' \
                ' \''+str(last_sync)+'\' AND \''+str(current_time)+'\' '

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        cur.execute(query)
        data = cur.fetchall()

        if not data:
            behavee_synchronizer.last_product_synchronization = current_time
            db.session.commit()
            return 0

        site_ids = set(product[10] for product in data)
        product_sku_set = set(product[0] for product in data)
        product_sku_name_set = set(product[1] for product in data)

        sites = db.session.query(BehaveeSite)\
            .filter(BehaveeSite.tracking_site_id.in_(list(site_ids))).all()

        if not sites:
            return 'no behavee sites in database'

        site_dict = {
            0: None
        }
        tracking_site_dict = {
            0: None
        }

        for site in sites:

            site_id = site.tracking_site_id
            partner_id = site.partner_id

            if not site.partner_id:
                partner = Partner(name=site.site_name)
                partner.behavee_site.append(site)
                db.session.add(partner)
                db.session.flush()
                partner_id = partner.id

            tracking_site_dict[site.tracking_site_id] = site_id
            site_dict[site_id] = partner_id

        product_skus = db.session.query(ProductSku.id, ProductSku.product_sku, ProductSku.product_sku_name) \
            .filter(ProductSku.product_sku.in_(product_sku_set)) \
            .filter(ProductSku.product_sku_name.in_(product_sku_name_set)).all()

        product_sku_dict = {}
        for sku in product_skus:
            product_sku_dict[(sku[1], sku[2])] = sku[0]

        products = db.session.query(Product.id, Product.name)\
            .filter(Product.name.in_(product_sku_set)).all()
        product_dict = {}
        for product in products:
            product_dict[product[1]] = product[0]

        bulk_commit_list = []
        product_list = []
        add_commit_list = []
        product_commit_dict = {}

        def sort_product_tracking_record(product):
            prod_record = ProductTrackingRecord(
                product_sku_id=product_sku_dict[(product[0], product[1])],
                visitor_tracking_id=product[7],
                product_sku=product[0],
                product_sku_name=product[1],
                timestamp=product[4],
                price=product[2],
                visit_tracking_id=product[8],
                quantity=product[9],
                site_id=check_if_exist(tracking_site_dict, product[10])
            )

            # idorder = 5
            # deleted = 6

            # product puchase - 5 != 0 and 6 == 0
            # produch refusal - 5 != 0 and 6 == 1
            # product in basket - 5 == 0 and 6 == 0
            # product out basket - 5 == 0 and 6 == 1

            if str(product[5]) != '0' and str(product[6]) == '0':  # product purchase
                prod_record.type = post_type(PRODUCT_TRACKING_TYPE,'purchase')
                prod_record.order_id = product[5]

            if str(product[5]) != '0' and str(product[6]) == '1':  # product refusal
                prod_record.type = post_type(PRODUCT_TRACKING_TYPE,'refusal')
                prod_record.order_id = product[5]

            if str(product[5]) == '0' and str(product[6]) == '0':  # product in basket
                prod_record.type = post_type(PRODUCT_TRACKING_TYPE,'in_basket')
                prod_record.order_id = product[5]

            if str(product[5]) == '0' and str(product[6]) == '1':  # product out basket
                prod_record.type = post_type(PRODUCT_TRACKING_TYPE,'out_basket')
                prod_record.order_id = product[5]

            bulk_commit_list.append(prod_record)
            return True

        for product in data:

            # if product_sku exist - add tracking record
            # if not exist, check if product exist, then add product_sku and tracking record
            # else add product, product_sku and tracking record

            if (product[0], product[1]) in product_sku_dict.keys():
                sort_product_tracking_record(product)

            elif product[0] in product_dict.keys():
                new_product_sku = ProductSku(
                    product_sku=product[0],
                    product_sku_name=product[1],
                    price=product[2],
                    product_id=product_dict[product[0]]
                )
                db.session.add(new_product_sku)
                db.session.flush()
                product_sku_dict[product[0], product[1]] = new_product_sku.id

                sort_product_tracking_record(product)

            else:
                new_product = Product(
                    name=product[0],
                    description=product[0],
                    active=1
                )
                new_product_sku = ProductSku(
                    product_sku=product[0],
                    product_sku_name=product[1],
                    price=product[2],
                )
                new_product.product_sku.append(new_product_sku)
                db.session.add(new_product_sku)
                db.session.flush()

                product_partner = ProductPartner(
                    product_id = new_product.id,
                    partner_id = check_if_exist(site_dict, product[10])
                )
                db.session.add(product_partner)
                db.session.flush()

                product_sku_dict[product[0], product[1]] = new_product_sku.id
                product_dict[product[0]] = new_product.id

                add_commit_list.append(new_product)
                sort_product_tracking_record(product)


        # update prices
        for item in add_commit_list:
            prices = []
            if item.product_sku:
                for sku in item.product_sku:
                    prices.append(float(sku.price))

            item.average_price = sum(prices) / float(len(prices))
            item.highest_price = max(prices)
            item.lowest_price = min(prices)

        db.session.bulk_save_objects(bulk_commit_list)
        behavee_synchronizer.last_product_synchronization = current_time
        db.session.commit()

        return 0

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


def sync_visitor_tracking_record(days, site_id, sync_id):
    '''
    :param days: how many days synchronizes in one function call
    :param site_id: site id which visitors should be synchronized
    :param sync_id: behavee synchronizer id - to read last sync timestamp, and save current sync timestamp
    synchronizes visits from matomo to backend db for given site and number of days
    '''
    try:
        if not days:
            return 'add arg1 - days'

        if not site_id:
            return 'add arg2 - site id'

        if not sync_id:
            return 'add arg3 - sync id'

        if int(days) > 7:
            return 'cant synchronize more then 7 days at once'

        start_time = time.time()
        behavee_synchronizer = db.session.query(BehaveeSynchronizer) \
            .filter(BehaveeSynchronizer.id == sync_id).first()

        if not behavee_synchronizer:
            return 'could not load last time synchronization'

        last_sync = behavee_synchronizer.last_visitor_synchronization
        try:
            current_time = last_sync + timedelta(days=int(days))
        except:
            return 'arg1 is not inteeger'

        now = dt.datetime.now()

        if (last_sync + timedelta(minutes=1)) > now:
            return 'synchronization done to current time'

        if now < current_time:
            current_time = now

        query = 'SELECT lv.idsite, lv.visit_first_action_time, lv.visit_last_action_time, lv.visit_total_time, ' \
                'lv.visit_goal_buyer, lv.visit_goal_converted, la_en.name, la_ex.name, lv.visit_total_actions, ' \
                'lv.config_browser_name, lv.location_browser_lang, lv.config_browser_version, lv.config_browser_engine, ' \
                'lv.config_device_brand, lv.config_device_model, lv.config_device_type, lv.config_os, lv.config_resolution, ' \
                'lv.location_city, lv.location_country, lv.location_latitude, lv.location_longitude, hex(lv.idvisitor), ' \
                'lv.idvisit, inet_ntoa(conv(hex(location_ip), 16, 10)) AS location_ip ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_en ' \
                'ON lv.visit_entry_idaction_url = la_en.idaction ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_ex ' \
                'ON lv.visit_exit_idaction_url = la_ex.idaction ' \
                'WHERE idsite = '+str(site_id)+' AND lv.visit_last_action_time BETWEEN ' \
                ' \'' + str(last_sync) + '\' AND \'' + str(current_time) + '\' '

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        cnx.close()

        if not data:
            print('no data')
            behavee_synchronizer.last_visitor_synchronization = current_time
            db.session.commit()
            return 0

        site_ids = set(visitor[0] for visitor in data)
        sites = db.session.query(BehaveeSite) \
            .filter(BehaveeSite.tracking_site_id.in_(list(site_ids))).all()

        if not sites:
            return 'no behavee sites in database'

        site_dict = {
            0: None
        }

        for site in sites:
            site_dict[site.tracking_site_id] = site.id

        commit_tracking_record = []
        commit_device = []
        commit_geolocation = []
        commit_ip_address = []

        for visit in data:
            visitor_tracking_record = VisitorTrackingRecord(
                site_id=check_if_exist(site_dict, visit[0]),
                from_timestamp=visit[1],
                to_timestamp=visit[2],
                visit_total_time=visit[3],
                visit_goal_buyer=visit[4],
                visit_goal_converted=visit[5],
                visit_entry_url=visit[6],
                visit_exit_url=visit[7],
                visitor_journey_count=visit[8],
                browser_name=visit[9],
                browser_language=visit[10],
                browser_version=visit[11],
                browser_engine=visit[12],
                visitor_tracking_id=visit[22],
                visit_tracking_id=visit[23]
            )

            device = Device(
                name=visit[14],
                description=visit[15],
                operating_system=visit[16],
                resolution=visit[17],
                visit_tracking_id=visit[23]
            )

            geo_location = GeoLocation(
                city=visit[18],
                country=visit[19],
                latitude=visit[20],
                longitude=visit[21],
                visit_tracking_id=visit[23],
                geo_location_type=post_type(GEO_LOCATION_TYPE, 'personal')
            )

            ip_address = IPAddress(
                visit_tracking_id=visit[23],
                ip_address=visit[24]
            )

            commit_tracking_record.append(visitor_tracking_record)
            commit_device.append(device)
            commit_geolocation.append(geo_location)
            commit_ip_address.append(ip_address)

        db.session.bulk_save_objects(commit_tracking_record)
        db.session.bulk_save_objects(commit_device)
        db.session.bulk_save_objects(commit_geolocation)
        db.session.bulk_save_objects(commit_ip_address)
        behavee_synchronizer.last_visitor_synchronization = current_time
        db.session.commit()
        return 0

    except:
        return 'something went wrong'


def sync_products(sync_id):
    '''
    function that synchronizes product data from matomo to backend
    '''

    start_time = time.time()
    behavee_synchronizer = db.session.query(BehaveeSynchronizer) \
        .filter(BehaveeSynchronizer.id == sync_id).first()

    current_time = dt.datetime.now()
    if not behavee_synchronizer:
        return 'could not load behavee synchronizer'

    last_sync = behavee_synchronizer.last_product_synchronization
    sites = db.session.query(BehaveeSite).all()

    if not sites:
        return 'no behavee sites in database'

    try:
        for site in sites:

            site_id = site.tracking_site_id
            partner_id = site.partner_id

            if not site.partner_id:

                partner = Partner(name=site.site_name)
                partner.behavee_site.append(site)
                db.session.add(partner)
                db.session.flush()
                partner_id = partner.id

            step_size = 10000
            limit = step_size
            offset = 0
            while True:
                #print('querying with limit '+str(limit)+' & offset '+str(offset))
                query = 'SELECT la_name.name, la_sku.name, lci.price, lci.quantity, lci.server_time, '\
                        'lci.idorder, lci.deleted, HEX(lci.idvisitor), lci.idvisit, lci.quantity ' \
                        'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_conversion_item` lci ' \
                        'JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_name ' \
                        'ON lci.idaction_name = la_name.idaction ' \
                        'JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_sku ' \
                        'ON lci.idaction_sku = la_sku.idaction ' \
                        'WHERE lci.idsite = \''+str(site_id)+'\' AND lci.server_time BETWEEN ' \
                        ' \''+str(last_sync)+'\' AND \''+str(current_time)+'\' ' \
                        'LIMIT '+str(offset)+','+str(limit)+' '

                cnx = mysql.connector.connect(**config)
                cur = cnx.cursor(buffered=True)

                cur.execute(query)
                data = cur.fetchall()

                if not data:
                    break

                product_sku_set = set(product[0] for product in data)
                product_sku_name_set = set(product[1] for product in data)

                product_skus = db.session.query(ProductSku.id, ProductSku.product_sku, ProductSku.product_sku_name) \
                    .filter(ProductSku.product_sku.in_(product_sku_set)) \
                    .filter(ProductSku.product_sku_name.in_(product_sku_name_set)).all()

                product_sku_dict = {}
                for sku in product_skus:
                    product_sku_dict[(sku[1], sku[2])] = sku[0]

                products = db.session.query(Product.id, Product.name)\
                    .filter(Product.name.in_(product_sku_set)).all()
                product_dict = {}
                for product in products:
                    product_dict[product[1]] = product[0]

                bulk_commit_list = []
                product_list = []
                add_commit_list = []
                product_commit_dict = {}

                def sort_product_tracking_record(product):
                    prod_record = ProductTrackingRecord(
                        product_sku_id=product_sku_dict[(product[0], product[1])],
                        visitor_tracking_id=product[7],
                        product_sku=product[0],
                        product_sku_name=product[1],
                        timestamp=product[4],
                        price=product[2],
                        visit_tracking_id=product[8],
                        quantity=product[9]
                    )

                    # idorder = 5
                    # deleted = 6

                    # product puchase - 5 != 0 and 6 == 0
                    # produch refusal - 5 != 0 and 6 == 1
                    # product in basket - 5 == 0 and 6 == 0
                    # product out basket - 5 == 0 and 6 == 1

                    if str(product[5]) != '0' and str(product[6]) == '0':  # product purchase
                        prod_record.type = post_type(PRODUCT_TRACKING_TYPE,'purchase')
                        prod_record.order_id = product[5]

                    if str(product[5]) != '0' and str(product[6]) == '1':  # product refusal
                        prod_record.type = post_type(PRODUCT_TRACKING_TYPE, 'refusal')
                        prod_record.order_id = product[5]

                    if str(product[5]) == '0' and str(product[6]) == '0':  # product in basket
                        prod_record.type = post_type(PRODUCT_TRACKING_TYPE, 'in_basket')
                        prod_record.order_id = product[5]

                    if str(product[5]) == '0' and str(product[6]) == '1':  # product out basket
                        prod_record.type = post_type(PRODUCT_TRACKING_TYPE, 'out_basket')
                        prod_record.order_id = product[5]

                    bulk_commit_list.append(prod_record)
                    return True

                for product in data:

                    # if product_sku exist - add tracking record
                    # if not exist, check if product exist, then add product_sku and tracking record
                    # else add product, product_sku and tracking record

                    if (product[0], product[1]) in product_sku_dict.keys():
                        sort_product_tracking_record(product)

                    elif product[0] in product_dict.keys():
                        new_product_sku = ProductSku(
                            product_sku=product[0],
                            product_sku_name=product[1],
                            price=product[2],
                            product_id=product_dict[product[0]]
                        )
                        db.session.add(new_product_sku)
                        db.session.flush()
                        product_sku_dict[product[0], product[1]] = new_product_sku.id

                        sort_product_tracking_record(product)

                    else:
                        new_product = Product(
                            name=product[0],
                            description=product[0],
                            active=1
                        )
                        new_product_sku = ProductSku(
                            product_sku=product[0],
                            product_sku_name=product[1],
                            price=product[2],
                        )
                        new_product.product_sku.append(new_product_sku)
                        db.session.add(new_product_sku)
                        db.session.flush()

                        product_partner = ProductPartner(
                            product_id = new_product.id,
                            partner_id = partner_id
                        )
                        db.session.add(product_partner)
                        db.session.flush()

                        product_sku_dict[product[0], product[1]] = new_product_sku.id
                        product_dict[product[0]] = new_product.id

                        add_commit_list.append(new_product)

                        sort_product_tracking_record(product)


                # update prices
                for item in add_commit_list:
                    prices = []
                    if item.product_sku:
                        for sku in item.product_sku:
                            prices.append(float(sku.price))

                    item.average_price = sum(prices) / float(len(prices))
                    item.highest_price = max(prices)
                    item.lowest_price = min(prices)

                db.session.bulk_save_objects(bulk_commit_list)
                db.session.commit()

                offset = offset + step_size

        sync_product_skus_attributes()
        sync_products_attributes()

        return 'products synchronization done'

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


def sync_visitor(site_id, limit, offset):
    '''
    function that synchronizes visitor data from matomo to backend
    '''

    if not site_id or not limit or not offset:
        return 'error: not all parameters were given'

    try:

        start_time = time.time()
        behavee_synchronizer = db.session.query(BehaveeSynchronizer) \
            .filter(BehaveeSynchronizer.id == 1).first()

        current_time = dt.datetime.now()
        if not behavee_synchronizer:

            return False

        last_sync = behavee_synchronizer.last_visitor_synchronization
        start_time_sort = time.time()

        query = 'SELECT lv.idsite, lv.visit_first_action_time, lv.visit_last_action_time, lv.visit_total_time, '\
                'lv.visit_goal_buyer, lv.visit_goal_converted, la_en.name, la_ex.name, lv.visit_total_actions, ' \
                'lv.config_browser_name, lv.location_browser_lang, lv.config_browser_version, lv.config_browser_engine, ' \
                'lv.config_device_brand, lv.config_device_model, lv.config_device_type, lv.config_os, lv.config_resolution, ' \
                'lv.location_city, lv.location_country, lv.location_latitude, lv.location_longitude, hex(lv.idvisitor), ' \
                'lv.idvisit ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_en ' \
                'ON lv.visit_entry_idaction_url = la_en.idaction ' \
                'LEFT JOIN `' + app.config.MATOMO_DATABASE_NAME + '`.`log_action` la_ex ' \
                'ON lv.visit_exit_idaction_url = la_ex.idaction ' \
                'WHERE lv.idsite = \'' + str(site_id) + '\' AND lv.visit_last_action_time BETWEEN ' \
                ' \'' + str(last_sync) + '\' AND \'' + str(current_time) + '\' ' \
                'LIMIT ' + str(offset) + ',' + str(limit) + ' '

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)

        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        cnx.close()

        if not data:
            return 2


        commit_tracking_record = []
        commit_device = []
        commit_geolocation = []

        for visit in data:

            visitor_tracking_record = VisitorTrackingRecord(
                site_id = site_id,
                from_timestamp = visit[1],
                to_timestamp = visit[2],
                visit_total_time = visit[3],
                visit_goal_buyer = visit[4],
                visit_goal_converted = visit[5],
                visit_entry_url = visit[6],
                visit_exit_url = visit[7],
                visitor_journey_count = visit[8],
                browser_name = visit[9],
                browser_language = visit[10],
                browser_version = visit[11],
                browser_engine = visit[12],
                visitor_tracking_id = visit[22],
                visit_tracking_id = visit[23]
            )

            device = Device(
                name = visit[14],
                description = visit[15],
                operating_system = visit[16],
                resolution = visit[17],
                visit_tracking_id=visit[23]
            )

            geo_location = GeoLocation(
                city=visit[18],
                country=visit[19],
                latitude=visit[20],
                longitude=visit[21],
                visit_tracking_id=visit[23],
                geo_location_type=post_type(GEO_LOCATION_TYPE, 'personal')
            )

            commit_tracking_record.append(visitor_tracking_record)
            commit_device.append(device)
            commit_geolocation.append(geo_location)
        start_time_commit = time.time()
        db.session.bulk_save_objects(commit_tracking_record)
        db.session.bulk_save_objects(commit_device)
        db.session.bulk_save_objects(commit_geolocation)
        db.session.commit()

        return 0

    except:
      return 'something went wrong'


def create_synchronizer(sync_id):
    '''
    :param sync_id: synchronizer id to create
    create a Behavee Synchronizer with given id
    '''
    print('sync')
    if not sync_id:
        return 'add arg1 sync id'

    synchronizer = BehaveeSynchronizer(
        id=sync_id,
        last_visitor_synchronization = '2018-01-01 00:00:00',
        last_site_synchronization = '2018-01-01 00:00:00',
        last_product_synchronization = '2018-01-01 00:00:00',
        last_partner_synchronization = '2018-01-01 00:00:00',
        last_user_synchronization = '2018-01-01 00:00:00'
    )
    try:
        db.session.add(synchronizer)
        db.session.commit()
    except exc.IntegrityError as e:
        db.session.rollback()
        return 'Error on flush - '+str(e)
    return 0


def delete_synchronizer(sync_id):
    '''
    :param sync_id: synchronizer id to delete
    delete a Behavee Synchronizer with given id
    '''
    if not sync_id:
        return 'add arg1 sync id'

    try:
        synchronizer = db.session.query(BehaveeSynchronizer)\
            .filter(BehaveeSynchronizer.id == sync_id).delete()

        if synchronizer == 0:
            return 'synchronizer with id '+str(sync_id)+' not found'

        db.session.commit()
    except exc.IntegrityError as e:
        db.session.rollback()
        return 'Error on flush - '+str(e)
    return 0


def add_site_partner(site_id, partner_id):
    '''
    :param site_id: site id
    :param partner_id: partner id
    add partner to given site
    '''
    if not site_id:
        return 'add site id'

    if not partner_id:
        return 'add partner id'

    partner = db.session.query(Partner)\
        .filter(Partner.id == partner_id).first()

    if not partner:
        return 'partner not found'

    site = db.session.query(BehaveeSite)\
        .filter(BehaveeSite.id == site_id).first()

    if not site:
        return 'site not found'

    site.partner_id = partner_id
    db.session.commit()
    return 0
