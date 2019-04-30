from app import db
from flask import request, abort
import mysql.connector
import json
import app.config
import datetime, sys
from werkzeug.exceptions import BadRequest


# Query Matomo - Behavee database
def getLastLocation(token_auth, visitor_id):
    try:
        config = {
            'user': app.config.MATOMO_DATABASE_USER,
            'password': app.config.MATOMO_DATABASE_PASS,
            'host': app.config.MATOMO_DATABASE_HOST,
            'port': app.config.MATOMO_DATABASE_PORT,
            'database': app.config.MATOMO_DATABASE_NAME,
            'connection_timeout': 5,
        }
        query = 'SELECT ' \
                'lv.visit_last_action_time, ' \
                'lv.idsite, inet_ntoa(conv(hex(location_ip), 16, 10)) AS location_ip, ' \
                'lv.location_browser_lang, lv.location_country, lv.location_region, lv.location_city, ' \
                'lv.location_latitude, lv.location_longitude ' \
                'FROM `' + app.config.MATOMO_DATABASE_NAME + '`.`log_visit` lv  ' \
                'WHERE lv.idvisitor = UNHEX(\''+visitor_id+'\') ' \
                'AND idsite IN (SELECT idsite FROM ' \
                '`' + app.config.MATOMO_DATABASE_NAME + '`.`access` da, ' \
                '`' + app.config.MATOMO_DATABASE_NAME + '`.`user` du ' \
                ' WHERE da.login = du.login ' \
                'AND du.superuser_access = 0 AND du.token_auth=\''+token_auth+'\') ' \
                'ORDER BY lv.idvisit'
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(buffered=True)
        cur.execute(query)

        # fetch all of the rows from the query
        data = cur.fetchall()

        value = {
            'visitor_id': visitor_id,
            'site_id': None,
            'location_ip': None,
            'location_browser_lang': None,
            'location_country': None,
            'location_region': None,
            'location_city': None,
            'location_latitude': None,
            'location_longitude': None,
            'visit_last_action_time': None
        }

        if len(data) > 0:
            for row in data:
                value = {
                    'visitor_id': visitor_id,
                    'site_id':  str(row[1]) ,
                    'location_ip':  str(row[2]) ,
                    'location_browser_lang':  str(row[3]) ,
                    'location_country':  str(row[4]) ,
                    'location_region':  str(row[5]) ,
                    'location_city':  str(row[6]) ,
                    'location_latitude':  str(row[7]) ,
                    'location_longitude':  str(row[8]) ,
                    'visit_last_action_time':  str(row[0])
                }
        cur.close()
        cnx.close()
        rtrn = json.dumps(value)
        return json.loads(rtrn)

    except mysql.connector.Error:
        e = BadRequest('Connection Error')
        e.code = 503
        e.data = {'visitorid': visitor_id, 'value': 'Connection Error'}
        raise e
    except:
        e = BadRequest('Service Unavailable')
        e.code = 503
        e.data = {'id': visitor_id, 'value': 'Error'}
        raise e
