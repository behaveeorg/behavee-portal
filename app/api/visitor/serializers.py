from flask_restplus import fields
from app.api.restplus import api

logvisit_location = api.model('Visitor\'s last location', {
    'visitor_id': fields.String(readOnly=True, description='a visitor ID (an 8 byte binary string)'),
    'site_id': fields.String(readOnly=True, description='the ID of the website it was tracked for'),
    'location_ip': fields.String(readOnly=True, description='the IP address of the computer that the visit was made from. Can be anonymized'),
    'location_browser_lang': fields.String(readOnly=True, description='a string describing the language used in the visitor\'s browser'),
    'location_country': fields.String(readOnly=True, description='a two character string describing the country the visitor was located in while visiting the site.'),
    'location_region': fields.String(readOnly=True, description='a two character string describing the region of the country the visitor was in.'),
    'location_city': fields.String(readOnly=True, description='a string naming the city the visitor was in while visiting the site.'),
    'location_latitude': fields.Float(readOnly=True, description='the latitude of the visitor while he/she visited the site.'),
    'location_longitude': fields.Float(readOnly=True, description='the longitude of the visitor while he/she visited the site.'),
    'visit_last_action_time': fields.String(readOnly=True, description='time, when visitor\'s last visited the site.'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_logvisit = api.inherit('Page of Visitors details', pagination, {
    'items': fields.List(fields.Nested(logvisit_location))
})