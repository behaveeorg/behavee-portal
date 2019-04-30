from flask_restplus import Api, Namespace, Resource
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
from flask import Flask, request, abort
import xmltodict
import json
import requests
import werkzeug
import functools
import logging

from app.config import _load_this_env
from app.api.restplus import api
from app.api.behavee.parsers import e404
from app.api.behavee.serializers import get_partners_serializer, post_partners_serializer, \
    get_partner_serializer, put_partners_serializer, delete_partner_serializer, get_products_serializer, \
    post_products_serializer, get_product_serializer, get_product_catalog, post_product_catalog, \
    get_visitors_serializer, get_visitor_serializer, put_product_serializer, \
    delete_product_serializer, get_product_statistics, get_sites_serializer, get_site_serializer, \
    put_site_serializer, delete_site_serializer, get_product_categories_serializer, \
    get_product_category_serializer, post_product_categories, put_visitor_serializer, \
    get_visitors_statistics_serializer, get_visitor_tracking_record_serializer, \
    get_product_tracking_record_serializer, get_partner_products_statistics_serializer

from app.api.behavee.business import authorize, get_partners, post_partner, get_partner, \
    put_partner, delete_partner, post_partners_products, get_partner_products, \
    get_partner_product_catalog, post_partner_product_catalog, get_partner_product_productsku, get_partner_product, \
    put_partner_product, delete_partner_product, get_partner_product_statistics, \
    get_partner_product_category, get_partner_product_categories, post_partner_product_categories, \
    get_partner_visitors, get_partner_visitor, put_partner_visitor, \
    get_partner_site, put_partner_site, get_partner_sites, delete_partner_site, get_number_visits, \
    get_partner_number_visits, get_partner_visitor_statistics, get_partner_product_tracking_record, \
    get_partner_visitor_tracking_record, post_sites, get_partner_offers, get_partner_offer, \
    get_partner_products_statistics

from .. import parsers
from app.api.behavee.behavee_sync_wrapper import sync_manager

log = logging.getLogger(__name__)
ns = Namespace('behavee', path='/partners', description='behavee namespace')

ok = 'OK'
unauthorized = 'Unauthorized'
forbidden = 'Forbidden'
not_found = 'Not Found'
service_unavailable = 'Service Unavailable'


@ns.route('/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class Partners(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_partners_serializer, skip_none=True)
    def get(self):
        """
        return a list of partners
        """

        token_auth = request.headers['token_auth']
        try: search_text = request.args.get('search')
        except: search_text = None

        return get_partners(token_auth, search_text)


    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(post_partners_serializer, skip_none=True)
    def post(self):
        """
        Upload a new Partner
        """

        try: args = request.get_json()
        except: args = None
        token_auth = request.headers['token_auth']
        return post_partner(token_auth, args)


@ns.route('/<string:partner_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class Partner(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_partner_serializer, skip_none=True)
    def get(self, partner_id):
        """
        will return partner with specific id
        """

        token_auth = request.headers['token_auth']
        return get_partner(token_auth, partner_id)

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(put_partners_serializer, skip_none=True)
    def put(self, partner_id):
        """
        update partner with specific id
        """

        token_auth = request.headers['token_auth']
        try: args = request.get_json()
        except: args = None

        return put_partner(token_auth, partner_id, args)


    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(delete_partner_serializer, skip_none=True)
    def delete(self, partner_id):
        """
        delete partner with specific id
        """

        token_auth = request.headers['token_auth']
        return delete_partner(token_auth, partner_id)


@ns.route('/<string:partner_id>/products/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProducts(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_products_serializer, skip_none=True)
    def get(self, partner_id):
        """
        return products of specific partner
        """

        token_auth = request.headers['token_auth']
        try: search_text = request.args.get('search')
        except: search_text = None

        return get_partner_products(partner_id, search_text, token_auth)


    @api.doc(parser=parsers.file_parser)
    @api.marshal_with(post_products_serializer, skip_none=True)
    def post(self, partner_id):
        """
        upload products to specific partner
        """

        token_auth = request.headers['token_auth']
        uploaded_file = request.files['xml_file']
        if uploaded_file.mimetype == 'text/xml':
            f = uploaded_file.read()
            try: pf = xmltodict.parse(f)
            except: pf = None
            return post_partners_products(partner_id, pf, token_auth)

        else:
            e404.data = {'message': 'Uploaded file is not XML'}
            raise e404


@ns.route('/<string:partner_id>/products/<int:product_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProduct(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_product_serializer, skip_none=True)
    def get(self, partner_id, product_id):
        """
        will return data of specific product
        """

        token_auth = request.headers['token_auth']
        return get_partner_product(partner_id, product_id, token_auth)

    # @api.doc(parser=parsers.token_parser)
    # @api.marshal_with(put_product_serializer, skip_none=False)
    # def put(self, partner_id, product_id):
    #     """
    #     update specific product
    #     """
    #
    #     token_auth = request.headers['token_auth']
    #
    #     try: product_data = request.get_json()
    #     except: product_data = None
    #
    #     return put_partner_product(partner_id, product_id, token_auth, product_data)

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(delete_product_serializer, skip_none=True)
    def delete(self, partner_id, product_id):
        """
        delete specific product
        """

        token_auth = request.headers['token_auth']
        return delete_partner_product(partner_id, product_id, token_auth)


@ns.route('/<string:partner_id>/products/<int:product_id>/statistics/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductStatistics(Resource):

    @api.doc(parser=parsers.date_parser)
    @api.marshal_with(get_product_statistics, skip_none=True)
    def get(self, partner_id, product_id):
        """
        return statistics of specific product
        """

        try: from_date = request.args['from_date']
        except: from_date = '2018-00-00'
        try: to_date = request.args['to_date']
        except: to_date = '2019-12-31'
        token_auth = request.headers['token_auth']

        return get_partner_product_statistics(partner_id, product_id, from_date, to_date, token_auth)


@ns.route('/<string:partner_id>/products/productCatalog/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductCatalog(Resource):

    @api.doc(parser=parsers.page_parser)
    @api.marshal_with(get_product_catalog, skip_none=True)
    def get(self, partner_id):
        """
        will return more products with limit and offset
        """

        try: limit = request.args['limit']
        except: limit = 0
        try: offset = request.args['offset']
        except: offset = 0
        auth_token = request.headers['token_auth']

        return get_partner_product_catalog(partner_id, auth_token, limit, offset)


    @api.doc(parser=parsers.file_parser)
    @api.marshal_with(post_product_catalog, skip_none=True)
    def post(self, partner_id):
        """
        upload products to specific partner
        """

        token_auth = request.headers['token_auth']
        uploaded_file = request.files['xml_file']
        if uploaded_file.mimetype == 'text/xml':
            f = uploaded_file.read()
            try: pf = xmltodict.parse(f)
            except: pf = None
            return post_partner_product_catalog(partner_id, pf, token_auth)

        else:
            e404.data = {'message': 'Uploaded file is not XML'}
            raise e404


@ns.route('/<string:partner_id>/products/productSKU/<int:product_sku>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductSku(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_product_serializer, skip_none=True)
    def get(self, partner_id, product_sku):
        """
        will return a product from database
        """

        auth_token = request.headers['token_auth']
        return get_partner_product_productsku(partner_id, product_sku, auth_token)


@ns.route('/<string:partner_id>/productsCategories/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductCategories(Resource):

    @api.doc(parser=parsers.page_parser)
    @api.marshal_with(get_product_categories_serializer, skip_none=True)
    def get(self, partner_id):
        """
        will return a product categories from database
        """

        try: limit = request.args['limit']
        except: limit = 0
        try: offset = request.args['offset']
        except: offset = 0
        auth_token = request.headers['token_auth']

        return get_partner_product_categories(partner_id, auth_token, limit, offset)

    @api.doc(parser=parsers.file_parser)
    @api.marshal_with(post_product_categories, skip_none=True)
    def post(self, partner_id):
        """
        post a new product categories
        """

        token_auth = request.headers['token_auth']
        uploaded_file = request.files['xml_file']
        if uploaded_file.mimetype == 'text/xml':
            f = uploaded_file.read()
            try: pf = xmltodict.parse(f)
            except: pf = None
            return post_partner_product_categories(partner_id, pf, token_auth)

        else:
            e404.data = {'message': 'Uploaded file is not XML'}
            raise e404


@ns.route('/<string:partner_id>/productsCategories/<int:product_category_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductCategory(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_product_category_serializer, skip_none=True)
    def get(self, partner_id, product_category_id):
        """
        will return a product from database
        """

        auth_token = request.headers['token_auth']
        return get_partner_product_category(partner_id, product_category_id, auth_token)


@ns.route('/<string:partner_id>/visitors/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerVisitors(Resource):

    @api.doc(parser=parsers.page_parser)
    @api.marshal_with(get_visitors_serializer, skip_none=True)
    def get(self, partner_id):
        """
        will return list of visitors
        """

        try: limit = request.args['limit']
        except: limit = 0
        try: offset = request.args['offset']
        except: offset = 0
        auth_token = request.headers['token_auth']
        try: search_text = request.args.get('search')
        except: search_text = None

        return get_partner_visitors(partner_id, search_text, auth_token, limit, offset)


@ns.route('/<string:partner_id>/visitors/<string:visitor_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerVisitor(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_visitor_serializer, skip_none=True)
    def get(self, partner_id, visitor_id):
        """
        will return data of specific visitor
        """

        token_auth = request.headers['token_auth']
        return get_partner_visitor(partner_id, visitor_id, token_auth)

    # @api.doc(parser=parsers.token_parser)
    # @api.marshal_with(put_visitor_serializer, skip_none=False)
    # def put(self, partner_id, visitor_id):
    #     """
    #     update specific visitor
    #     """
    #
    #     token_auth = request.headers['token_auth']
    #     try: visitor_data = request.get_json()
    #     except: visitor_data = None
    #
    #     return put_partner_visitor(partner_id, visitor_id, token_auth, visitor_data)


@ns.route('/<string:partner_id>/visitors/<string:visitor_id>/statistics/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerVisitorsStatistics(Resource):

    @api.doc(parser=parsers.date_parser)
    @api.marshal_with(get_visitors_statistics_serializer, skip_none=True)
    def get(self, partner_id, visitor_id):
        """
        return statistics of specific product
        """

        try: from_date = request.args['from_date']
        except: from_date = '2018-00-00'
        try: to_date = request.args['to_date']
        except: to_date = '2019-12-31'
        token_auth = request.headers['token_auth']

        return get_partner_visitor_statistics(partner_id, visitor_id, from_date, to_date, token_auth)


@ns.route('/<string:partner_id>/sites/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerSites(Resource):


    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_sites_serializer, skip_none=True)
    def get(self, partner_id):
        """
        will return a list of sites
        """

        token_auth = request.headers['token_auth']
        try: search_text = request.args.get('search')
        except: search_text = None

        return get_partner_sites(partner_id, search_text, token_auth)


    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(post_partners_serializer, skip_none=True)
    def post(self, partner_id):
        """
        Upload a new Site
        """

        args = json.loads(request.data)
        token_auth = request.headers['token_auth']
        return post_sites(token_auth, partner_id, args)


@ns.route('/<string:partner_id>/sites/<int:site_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerSite(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_site_serializer, skip_none=True)
    def get(self, partner_id, site_id):
        """
        will return data of specific site
        """

        token_auth = request.headers['token_auth']
        return get_partner_site(partner_id, site_id, token_auth)

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(put_site_serializer, skip_none=False)
    def put(self, partner_id, site_id):
        """
        update specific site
        """

        token_auth = request.headers['token_auth']
        try: args = request.get_json()
        except: args = None

        return put_partner_site(partner_id, site_id, token_auth, args)

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(delete_site_serializer, skip_none=True)
    def delete(self, partner_id, site_id):
        """
        delete specific site
        """

        auth_token = request.headers['token_auth']
        return delete_partner_site(partner_id, site_id, auth_token)


@ns.route('/visits_report/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class VisitsReports(Resource):

    @api.doc(parser=parsers.date_parser)
    def get(self):
        """
        will return list of partners and their sites along with visits and unique visits
        """

        try: from_date = request.args['from_date']
        except: from_date = '2018-00-00'
        try: to_date = request.args['to_date']
        except: from_date = '2018-01-00'

        auth_token = request.headers['token_auth']

        return get_number_visits(from_date, to_date, auth_token)


@ns.route('/synchronize/<int:sync_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class Synchronize(Resource):

    @api.doc(parser=parsers.token_parser)
    def get(self, sync_id):
        """
        synchronization endpoint for superusers only
        """
        try: arg1 = request.args['arg1']
        except: arg1 = None
        try: arg2 = request.args['arg2']
        except: arg2 = None
        try: arg3 = request.args['arg3']
        except: arg3 = None
        auth_token = request.headers['token_auth']

        return sync_manager(auth_token, sync_id, arg1, arg2, arg3)


@ns.route('/<string:partner_id>/visits_report/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class VisitsReport(Resource):

    @api.doc(parser=parsers.date_parser)
    def get(self, partner_id):
        """
        will return number of visits and unique visits for given date and partner
        """

        try: from_date = request.args['from_date']
        except: from_date = '2018-00-00'
        try: to_date = request.args['to_date']
        except: to_date = '2018-00-00'
        auth_token = request.headers['token_auth']

        return get_partner_number_visits(from_date, to_date, partner_id, auth_token)


@ns.route('/<string:partner_id>/visitors/<string:visitor_id>/<int:visitor_tracking_record_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerVisitorTrackingRecord(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_visitor_tracking_record_serializer, skip_none=True)
    def get(self, partner_id, visitor_id, visitor_tracking_record_id):
        """
        return specific visitor tracking record
        """

        token_auth = request.headers['token_auth']

        return get_partner_visitor_tracking_record(partner_id, visitor_id, visitor_tracking_record_id, token_auth)


@ns.route('/<string:partner_id>/products/<int:product_sku>/<int:product_tracking_record_id>/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductTrackingRecord(Resource):

    @api.doc(parser=parsers.token_parser)
    @api.marshal_with(get_product_tracking_record_serializer, skip_none=True)
    def get(self, partner_id, product_sku, product_tracking_record_id):
        """
        return specific visitor tracking record
        """

        token_auth = request.headers['token_auth']

        return get_partner_product_tracking_record(partner_id, product_sku, product_tracking_record_id, token_auth)


# @ns.route('/<string:partner_id>/offers/')
# @api.response(200, ok)
# @api.response(401, unauthorized)
# @api.response(403, forbidden)
# @api.response(404, not_found)
# @api.response(503, service_unavailable)
# class PartnerOffers(Resource):
#
#     @api.doc(parser=parsers.empty_parser)
#     def get(self, partner_id):
#         """
#        will return a list of offers
#         """
#
#         return get_partner_offers(partner_id)
#
#
# @ns.route('/<string:partner_id>/offers/<int:offer_id>/')
# @api.response(200, ok)
# @api.response(401, unauthorized)
# @api.response(403, forbidden)
# @api.response(404, not_found)
# @api.response(503, service_unavailable)
# class PartnerOffer(Resource):
#
#     @api.doc(parser=parsers.empty_parser)
#     def get(self, partner_id, offer_id):
#         """
#         will return a specific offer
#         """
#
#         return get_partner_offer(partner_id, offer_id)


@ns.route('/<string:partner_id>/partnerProductStatistics/')
@api.response(200, ok)
@api.response(401, unauthorized)
@api.response(403, forbidden)
@api.response(404, not_found)
@api.response(503, service_unavailable)
class PartnerProductsStatistics(Resource):

    @api.doc(parser=parsers.date_parser)
    @api.marshal_with(get_partner_products_statistics_serializer, skip_none=True)
    def get(self, partner_id):
        """
        will return a statistics for all sites that belong to given partner
        """

        try: from_date = request.args['from_date']
        except: from_date = None
        try: to_date = request.args['to_date']
        except: to_date = None

        token_auth = request.headers['token_auth']
        return get_partner_products_statistics(token_auth, partner_id, from_date, to_date)