from app import app, db
import time
import threading

from app.models.behavee import *
from app.models.matomo import MatomoUser
import mysql.connector
from sqlalchemy import or_, and_, exc, text
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import ImmutableMultiDict
from app.models.packages import PackageManager
from app.toolbox.matomo import SitesManager, MatomoError
from app.api.behavee.behavee_sync_wrapper import sync_site
from app.api.behavee.matomo import authorize, get_matomo_visitor_geolocation_device, \
    get_matomo_visitor_tracking_data, get_matomo_site, get_matomo_visitors, get_user_login, \
    number_of_visits, partner_number_of_visits, get_matomo_visitor_statistics, get_visitor_journey
from app.api.behavee.parsers import e401, e404, e500
from app.constants import media_types, PARTNER_TYPE, DEVICE_TYPE, LANGUAGES, VISITOR_TYPE, GEO_LOCATION_TYPE, \
    CONTENT_TYPE, MEDIA_TYPE, CONTACT_TYPE, SITE_TYPE, CURRENCY, PRODUCT_TRACKING_TYPE
from .toolbox import check_if_exist, check_type, get_type, post_type, price_check, get_att_list, \
    delete_lists_duplicates
from .behavee_sync_wrapper import sync_visitor_attributes, sync_products_attributes


def get_partners(token_auth, search_text):
    '''
    :param token_auth: user's autentication token
    :param search_text: #TODO should be used to search in partners database data
    :return: a list of partners
    '''


    login = get_user_login(token_auth)
    if not login:
        raise e401

    return_dict = {}

    partner_data = db.session.query(Partner) \
        .outerjoin(PartnerUserRel) \
        .filter(Partner.deleted == False) \
        .filter(PartnerUserRel.matomo_user_id == login).all()

    if partner_data:
        try:
            partner_list = []

            for partner in partner_data:
                partner_dict = {
                    'id': partner.uuid,
                    'name': partner.name,
                    'description': partner.description,
                    'type': partner.get_partner_type()
                }
                partner_list.append(partner_dict)

            return_dict['partners'] = partner_list

        except:
            e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
            raise e500


    elif(authorize(token_auth)):
        e404.data = {'message': 'no partners in database which you are autorized to view'}
        raise e404

    else:
        raise e401

    return return_dict


def post_partner(token_auth, args):
    '''
       :param token_auth: user's autentiocation token
       :param partner_id: id of partner which will be edited
       :param put_partner_data: edited data of partner in JSON
       :return: update status and data from get_partner function for this partner
       '''

    if args is None:
        e404.data = {'Error': 'Json data in request\'s body expected'}
        raise e404

    login = get_user_login(token_auth)
    if not login:
        raise e401

    try:
        errors = []
        partner = Partner()

        try:
            partner.name = args['name']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s name is required'})

        try:
            partner.description = args['description']
        except KeyError:  # not required
            pass

        try:
            partner.company_number = args['company_number']
        except KeyError:  # not required
            pass

        try:
            partner.vat_number = args['vat_number']
        except KeyError:  # not required
            pass

        try:
            partner.post_partner_type(args['partner_type'].lower())
        except KeyError:
            errors.append({'KeyError': 'Partner\'s type is required'})


        geo_location = GeoLocation()

        try:
            geo_location.post_geo_location_type(args['address_type'].lower())
        except KeyError:
            errors.append({'KeyError': 'Partner\'s address type is required'})

        try:
            geo_location.street = args['address_street']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s address street is required'})

        try:
            geo_location.street_no = args['address_street_no']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s address street No is required'})

        try:
            geo_location.zip_code = args['address_zip_code']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s address zip code is required'})

        try:
            geo_location.city = args['address_city']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s address city is required'})

        try:
            geo_location.country = args['address_country']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s address country is required'})

        partner.geo_location.append(geo_location)

        if len(errors) > 0:
            e404.data = errors
            raise e404

        db.session.add(partner)
        db.session.flush()

        rel = PartnerUserRel(matomo_user_id=login, partner_id=partner.id)
        db.session.add(rel)
        db.session.commit()

        return {'success': True}

    except:
        raise e500


def get_partner(token_auth, partner_id):
    '''
    :param token_auth: user's autentication token
    :param partner_id: id of partner which data will be returned from database
    :return: a dictionary of partner data from database
    '''

    login = get_user_login(token_auth)
    if not login:
        raise e401

    partner_data = db.session.query(Partner, GeoLocation, Crm, MarketSegment)\
        .outerjoin(Crm)\
        .outerjoin(MarketSegment)\
        .outerjoin(GeoLocation) \
        .filter(Partner.deleted == False)\
        .filter(Partner.uuid == partner_id).all()

    if partner_data:

        crm_dict = {}
        market_segment_dict = {}
        geo_location_list = []

        partner = partner_data[0][0]
        crm = partner_data[0][2]
        market_segment = partner_data[0][3]
        geo_locations = list(set(r[1] for r in partner_data))

        try:
            return_dict = {
                "id": partner.uuid,
                "name": partner.name,
                "description": partner.description,
                "companyNumber": partner.company_number,
                "vatNumber": partner.vat_number,
                "type": partner.get_partner_type(),
            }

            if crm:
                crm_dict = {
                    "id": crm.id,
                    "name": crm.name,
                    "description": crm.description
                }

            if market_segment:
                market_segment_dict = {
                    "id": market_segment.id,
                    "name": market_segment.name,
                    "description": market_segment.description
                }


            for geo_location in geo_locations:
                if geo_location:
                    geo_location_dict = {
                        "id": geo_location.id,
                        "type": geo_location.get_geo_location_type(),
                        "continent": geo_location.continent,
                        "continentCode": geo_location.continent_code,
                        "country": geo_location.country,
                        "countryCode": geo_location.country_code,
                        "city": geo_location.city,
                        "street": geo_location.street,
                        "streetNo": geo_location.street_no,
                        "zip": geo_location.zip_code,
                        "latitude": geo_location.latitude,
                        "longitude": geo_location.longitude,
                    }
                    geo_location_list.append(geo_location_dict)


            return_dict['crm'] = crm_dict
            return_dict['marketSegment'] = market_segment_dict
            return_dict['geoLocation'] = geo_location_list

        except:
            e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
            raise e500

    elif(authorize(token_auth)):
        e404.data = {'message': 'partner with id {} does not exist in database, or you are not authorized to view it'.format(partner_id)}
        raise e404

    else:
        raise e401

    return return_dict


def put_partner(token_auth, partner_id, args):
    '''
    :param token_auth: user's autentiocation token
    :param partner_id: id of partner which will be edited
    :param put_partner_data: edited data of partner in JSON
    :return: update status and data from get_partner function for this partner
    '''

    if args is None:
        e404.data = {'Error': 'Json data in request\'s body expected'}
        raise e404

    login = get_user_login(token_auth)
    if not login:
        raise e401

    partner_data = db.session.query(Partner)\
        .outerjoin(PartnerUserRel)\
        .filter(PartnerUserRel.matomo_user_id == login)\
        .filter(Partner.uuid == partner_id)\
        .filter(Partner.deleted == False).first()


    if not partner_data:
        e404.data = {'message': 'Partner with id {} does not exist '\
                                'or you are not authorized to edit it'.format(partner_id)}
        raise e404

    try:
        errors = []

        try: partner_data.name = args['name']
        except KeyError:
            errors.append({'KeyError': 'Partner\'s name is required'})

        try: partner_data.description = args['description']
        except KeyError: # not required
            pass

        try: partner_data.company_number = args['company_number']
        except KeyError:  # not required
            pass

        try: partner_data.vat_number = args['vat_number']
        except KeyError:  # not required
            pass

        try: partner_data.post_partner_type(args['partner_type'].lower())
        except KeyError:
            errors.append({'KeyError': 'Partner\'s type is required'})

        if len(partner_data.geo_location) > 0:
            try: partner_data.geo_location[0].post_geo_location_type(args['address_type'].lower())
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address type is required'})

            try: partner_data.geo_location[0].street = args['address_street']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address street is required'})

            try: partner_data.geo_location[0].street_no = args['address_street_no']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address street No is required'})

            try: partner_data.geo_location[0].zip_code = args['address_zip_code']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address zip code is required'})

            try: partner_data.geo_location[0].city = args['address_city']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address city is required'})

            try: partner_data.geo_location[0].country = args['address_country']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address country is required'})
        else:
            geo_location = GeoLocation()
            try:
                geo_location.post_geo_location_type(args['address_type'].lower())
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address type is required'})

            try:
                geo_location.street = args['address_street']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address street is required'})

            try:
                geo_location.street_no = args['address_street_no']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address street No is required'})

            try:
                geo_location.zip_code = args['address_zip_code']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address zip code is required'})

            try:
                geo_location.city = args['address_city']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address city is required'})

            try:
                geo_location.country = args['address_country']
            except KeyError:
                errors.append({'KeyError': 'Partner\'s address country is required'})

            partner_data.geo_location.append(geo_location)

        if len(errors) > 0:
            e404.data = errors
            raise e404
        else:
            db.session.commit()
            return {'success':True}

    except:
        raise e500


def delete_partner(token_auth, partner_id):
    '''
    :param token_auth: autentication token
    :param partner_id: id of partner which will be deleted
    :return: deletion status and data from get_partner function for this partner
    '''

    login = get_user_login(token_auth)
    if not login:
        raise e401

    partner_data = db.session.query(Partner)\
        .filter(Partner.deleted == False) \
        .filter(Partner.uuid == partner_id).first()

    if partner_data:
        partner_dict = get_partner(token_auth, partner_id)
        return_dict = {
            "deleted": partner_dict
        }

        partner_data.deleted = True;

        db.session.commit()

        return return_dict

    elif(authorize(token_auth)):
        e404.data = {'message': 'Partner with id {} does not exist in database or you are not authorized to delete it'.format(partner_id)}
        raise e404

    else:
        raise e401


def post_partners_products(partner_id, product_data, token_auth):
    '''
    older function for uploading product without [product_must, product_must_not, product_wished, product_spin_off]
    :param partner_id: id of the partner which will be the owner of this product
    :param product_data: data from XML file uploaded on endpoint
    :param token_auth: user's autentication token
    :return: list of product names and their status of database write
    '''

    start_time = time.time()
    return_dict = {
        'success': False,
        'products': 0,
        'productsSku': 0
    }
    prod_name = []
    commit_list = []
    product_dict = {}
    product_sku_dict = {}
    product_parameter_dict = {}
    product_media_dict = {}
    product_geolocation_dict = {}

    def get_data_from_xml(item):
        if item['NAME'] not in product_dict.keys():
            product_dict[item['NAME']] = Product(
                name=item['NAME'],
                description=item['DESCRIPTION'],
                active=True
            )
            prod_name.append(item['NAME'])

        if item['NAME'] in product_sku_dict.keys():
            product_sku_dict[item['NAME']].append(ProductSku(
                product_sku=item['NAME'],
                product_sku_name=item['DESCRIPTION'],
                price=item['PRICE']
            ))
        else:
            product_sku_dict[item['NAME']] = [ProductSku(
                product_sku=item['NAME'],
                product_sku_name=item['DESCRIPTION'],
                price=item['PRICE']
            )]

        # parameters, media and geolocation
        # sort geo_locations
        try:
            if type(item['ADDRESSES']['ADDRESS']) == list:
                for geo_location_item in item['ADDRESSES']['ADDRESS']:
                    geo_location = GeoLocation(country=address['COUNTRY'],
                                               street=address['STREET'],
                                               city=address['CITY'],
                                               zip_code=address['ZIP-CODE'],
                                               longitude=address['LONGITUDE'],
                                               latitude=address['LATITUDE'],
                                               geo_location_type=post_type(GEO_LOCATION_TYPE,
                                                                      'product_placement'))
                    if (item['NAME'], item['PRICE']) in product_geolocation_dict.keys():
                        product_geolocation_dict[(item['NAME'], item['PRICE'])].append(geo_location)
                    else:
                        product_geolocation_dict[(item['NAME'], item['PRICE'])] = [geo_location]

            elif item['ADDRESSES']['ADDRESS']:
                geo_location = GeoLocation(country=item['ADDRESSES']['ADDRESS']['COUNTRY'],
                                           street=item['ADDRESSES']['ADDRESS']['STREET'],
                                           city=item['ADDRESSES']['ADDRESS']['CITY'],
                                           zip_code=item['ADDRESSES']['ADDRESS']['ZIP-CODE'],
                                           longitude=item['ADDRESSES']['ADDRESS']['LONGITUDE'],
                                           latitude=item['ADDRESSES']['ADDRESS']['LATITUDE'],
                                           geo_location_type=post_type(GEO_LOCATION_TYPE, 'product_placement'))
                if (item['NAME'], item['PRICE']) in product_geolocation_dict.keys():
                    product_geolocation_dict[(item['NAME'], item['PRICE'])].append(geo_location)
                else:
                    product_geolocation_dict[(item['NAME'], item['PRICE'])] = [geo_location]

        except KeyError:
            pass

        # sort product parameter
        try:
            if type(item['PRODUCT_PARAM']) == list:
                for product_parameter_item in item['PRODUCT_PARAM']:
                    product_parameter = ProductParameter(name=product_parameter_item['PARAM_NAME'],
                                                         value=product_parameter_item['PARAM_VALUE'])
                    if (item['NAME'], item['PRICE']) in product_parameter_dict.keys():
                        product_parameter_dict[(item['NAME'], item['PRICE'])].append(product_parameter)
                    else:
                        product_parameter_dict[(item['NAME'], item['PRICE'])] = [product_parameter]

            elif item['PRODUCT_PARAM']:
                product_parameter = ProductParameter(name=item['PRODUCT_PARAM']['PARAM_NAME'],
                                                     value=item['PRODUCT_PARAM']['PARAM_VALUE'])
                if (item['NAME'], item['PRICE']) in product_parameter_dict.keys():
                    product_parameter_dict[(item['NAME'], item['PRICE'])].append(product_parameter)
                else:
                    product_parameter_dict[(item['NAME'], item['PRICE'])] = [product_parameter]

        except KeyError:
            pass

        # sort product media
        try:
            if type(item['CATALOG_SUBJECT_MEDIA']) == list:
                for product_media_item in item['CATALOG_SUBJECT_MEDIA']:
                    product_media = ProductMedia(type=post_type(MEDIA_TYPE, product_media_item['TYPE']),
                                                 url=product_media_item['URL'])
                    if (item['NAME'], item['PRICE']) in product_media_dict.keys():
                        product_media_dict[(item['NAME'], item['PRICE'])].append(product_media)
                    else:
                        product_media_dict[(item['NAME'], item['PRICE'])] = [product_media]


            elif item['CATALOG_SUBJECT_MEDIA']:
                product_media = ProductMedia(type=post_type(MEDIA_TYPE, item['CATALOG_SUBJECT_MEDIA']['TYPE']),
                                             url=item['CATALOG_SUBJECT_MEDIA']['URL'])
                if (item['NAME'], item['PRICE']) in product_media_dict.keys():
                    product_media_dict[(item['NAME'], item['PRICE'])].append(product_media)
                else:
                    product_media_dict[(item['NAME'], item['PRICE'])] = [product_media]

        except KeyError:
            pass

    def save_products_db():
        # prod_name - all unique names of uploading products
        # query the db and return all products that match name with some name from prod_name

        products = db.session.query(Product) \
            .filter(Product.name.in_(prod_name)).all()

        # create a list for existing products
        # product_dict - dictionary with all uploading products
        # pop products that exist in db from product_dict
        # result - products that already exist in existing_products, new products in product_dict
        existing_products = []

        for prod in products:
            if str(prod.name) in product_dict.keys():
                product_dict.pop(str(prod.name), None)
                existing_products.append(prod)

        # not exist - add all skus, commit, query, then add all other tables
        # get the new products from product_dict and upload it to db
        new_products = list(product_dict.values())
        db.session.bulk_save_objects(new_products)
        db.session.commit()

        return_dict['productsSku'] = len(new_products)

        # get the instances of new products
        new_products = db.session.query(Product) \
            .filter(Product.name.in_(list(product.name for product in new_products))).all()

        # new products in new_products
        # existing products in existing_products

        # for new products, match sku, commit to db, retrieve, add all other tables and commit
        # for existing products, match sku, check if they exist in db

        new_products_sku = []
        check_product_sku = []
        check_product_sku_dict = {}

        for product in existing_products:

            if product.name in product_sku_dict.keys():

                for product_sku in product_sku_dict[product.name]:
                    product_sku.product_id = product.id
                    check_product_sku_dict[(str(product_sku.product_sku), int(product_sku.price))] = product_sku

                check_product_sku.extend(product_sku_dict[product.name])
                product_sku_dict.pop(str(product.name), None)

        for product in new_products:

            if product.name in product_sku_dict.keys():

                for product_sku in product_sku_dict[product.name]:
                    product_sku.product_id = product.id

                new_products_sku.extend(product_sku_dict[product.name])
                product_sku_dict.pop(str(product.name), None)

            commit_list.append(ProductPartner(
                product_id=product.id,
                partner_id=partner.id
            ))

        # check product skus
        # commit new product skus

        # print(check_product_sku)
        existing_product_skus = db.session.query(ProductSku) \
            .filter(ProductSku.product_sku.in_(list(sku.product_sku for sku in check_product_sku))) \
            .filter(ProductSku.price.in_(list(sku.price for sku in check_product_sku))).all()

        for product_sku in existing_product_skus:

            if (str(product_sku.product_sku), int(product_sku.price)) in check_product_sku_dict.keys():
                check_product_sku_dict.pop((str(product_sku.product_sku), int(product_sku.price)), None)

        new_products_sku.extend(list(check_product_sku_dict.values()))

        db.session.bulk_save_objects(new_products_sku)
        db.session.commit()

        return_dict['productsSku'] = len(new_products_sku)

        # query for the new products_sku and add all other tables
        added_product_skus = db.session.query(ProductSku) \
            .filter(ProductSku.product_sku.in_(list(sku.product_sku for sku in new_products_sku))) \
            .filter(ProductSku.price.in_(list(sku.price for sku in new_products_sku))).all()

        # load others tables that belongs to sku, add sku.id to it and commit

        for product_sku in added_product_skus:

            tpl = (str(product_sku.product_sku), str(int(product_sku.price)))

            if tpl in product_geolocation_dict.keys():
                for geo_location in product_geolocation_dict[tpl]:
                    geo_location.product_sku_id = product_sku.id
                    commit_list.append(geo_location)

            if tpl in product_media_dict.keys():
                for media in product_media_dict[tpl]:
                    media.product_sku_id = product_sku.id
                    commit_list.append(media)

            if tpl in product_parameter_dict.keys():
                for parameter in product_parameter_dict[tpl]:
                    parameter.product_sku_id = product_sku.id
                    commit_list.append(parameter)

        db.session.bulk_save_objects(commit_list)
        db.session.commit()

    if authorize(token_auth):

        if product_data is None:
            e404.data = {'message': 'Xml file is empty or corrupted'}
            raise e404

        try:
            # get partner
            partner = db.session.query(Partner).filter(Partner.uuid == partner_id).first()

            if not partner:
                e404.data = {'message': 'Partner with id {} does not exist'.format(partner_id)}
                raise e404

            try: product_type = type(product_data['SHOP']['PRODUCT'])
            except KeyError:
                e404.data = {'message': 'XML keys [SHOP][PRODUCT] not found'}
                raise e404

            # multiple products in xml
            if product_type == list:

                for item in product_data['SHOP']['PRODUCT']:
                    get_data_from_xml(item)

            else:
                get_data_from_xml(product_data['SHOP']['PRODUCT'])

            save_products_db()
            return_dict['success'] = True

            thread = threading.Thread(target=sync_products_attributes, args=())
            thread.daemon = True
            thread.start()

            return return_dict

        except:
            e404.data = {'message': 'Error while parsing the xml file. Check the file structure'}
            raise e404

    else:
        raise e401


def get_partner_products(partner_id, search_text, token_auth):
    '''
    :param partner_id: id of partner
    :param search_text: #TODO should be able to filter the product with search_text
    :param token_auth: user's autentication token
    :return: a list of products
    '''

    login = get_user_login(token_auth)

    if not login:
        raise 401

    product_data = db.session.query(Product)\
        .join(ProductPartner)\
        .join(Partner)\
        .filter(Product.active == True) \
        .filter(Partner.uuid == partner_id).all()

    if product_data:

        try:
            product_list = []
            for product in product_data:
                product_dict = {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description
                }
                product_list.append(product_dict)

            return_dict = {
                "products": product_list
            }

        except:
            e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
            raise e500

    else:
        print('no data')
        e404.data = {'message': 'No products in database for partner {}'.format(partner_id)}
        raise e404

    return return_dict


def get_partner_product(partner_id, product_id, token_auth):
    def get_product_sku_sorted(product_skus):
        product_sku_list = []
        if product_skus:
            if product_skus[0] is not None:
                for product_sku in product_skus:
                    product_skus_dict = {
                        "id": product_sku.id,
                        "productSku": product_sku.product_sku,
                        "productSkuName": product_sku.product_sku_name,
                        "actionCategory1": product_sku.action_category1,
                        "actionCategory2": product_sku.action_category2,
                        "actionCategory3": product_sku.action_category3,
                        "actionCategory4": product_sku.action_category4,
                        "actionCategory5": product_sku.action_category5,
                        "price": product_sku.price,
                        "vat": product_sku.vat,
                        "currency": product_sku.get_product_sku_currency(),
                        'offeredFrom': product_sku.offered_from,
                        'firstPurchase': product_sku.first_purchase,
                        'lastPurchase': product_sku.last_purchase,
                        'noOfPurchases': product_sku.no_of_purchases,
                        'noOfRefusals': product_sku.no_of_refusals,
                        'noOfViews': product_sku.no_of_views,
                        'averageViewTime': product_sku.average_view_time
                    }
                    product_sku_list.append(product_skus_dict)
        return product_sku_list

    '''
    :param partner_id: id of partner
    :param product_id: id of products which data will be returned
    :param token_auth: user's autentication token
    :return: a dictionary of partner data along with other partner relationship tables
    '''

    login = get_user_login(token_auth)

    if not login:
        raise e401

    product_data = db.session.query(Product, Partner, ProductCategory, ProductMedia, ProductParameter, ProductSku)\
        .join(ProductPartner)\
        .join(Partner)\
        .filter(Product.id == product_id) \
        .filter(Product.active == True) \
        .filter(Partner.uuid == partner_id) \
        .outerjoin(ProductSku) \
        .outerjoin(ProductCategory) \
        .outerjoin(ProductMedia) \
        .outerjoin(ProductParameter) \
        .all()

    product = list(set(r[0] for r in product_data))
    partners = list(set(r[1] for r in product_data))
    product_categories = list(set(r[2] for r in product_data))
    product_medias = list(set(r[3] for r in product_data))
    product_parameters = list(set(r[4] for r in product_data))
    product_skus = list(set(r[5] for r in product_data))
    product_media_dict = {
        0: []
    }
    product_parameter_dict = {
        0: []
    }

    must_product_data = db.session.query(ProductSku)\
        .join(MustProduct)\
        .join(Product)\
        .filter(Product.id == product_id)\
        .all()
    must_not_product_data = db.session.query(ProductSku) \
        .join(MustNotProduct)\
        .join(Product)\
        .filter(Product.id == product_id) \
        .all()
    wished_product_data = db.session.query(ProductSku) \
        .join(WishedProduct)\
        .join(Product)\
        .filter(Product.id == product_id) \
        .all()
    spin_off_product_data = db.session.query(ProductSku) \
        .join(SpinOffProduct)\
        .join(Product)\
        .filter(Product.id == product_id) \
        .all()

    if product_data:
        try:
            return_dict = {
                "id": product[0].id,
                "name": product[0].name,
                "description": product[0].description,
                "lowestPrice": product[0].lowest_price,
                "highestPrice": product[0].highest_price,
                "averagePrice": product[0].average_price,
                "vat": product[0].vat,
                "currency": product[0].get_product_currency(),
                'offeredFrom': product[0].offered_from,
                'firstPurchase': product[0].first_purchase,
                'lastPurchase':  product[0].last_purchase,
                'noOfPurchases': product[0].no_of_purchases,
                'noOfRefusals': product[0].no_of_refusals,
                'noOfViews': product[0].no_of_views,
                'averageViewTime': product[0].average_view_time
            }

            partner_list = []

            for partner in partners:
                if partner:
                    partner_dict = {
                        "id": partner.uuid,
                        "name": partner.name,
                        "description:": partner.description,
                        "type": partner.get_partner_type()
                    }
                    partner_list.append(partner_dict)
            return_dict['partner'] = partner_list

            product_category_list = []
            for product_category in product_categories:
                if product_category:
                    product_category_dict = {
                        "id": product_category.id,
                        "segmentCode": product_category.segment_code,
                        "segmentDescription": product_category.segment_description,
                        "familyCode": product_category.family_code,
                        "familyDescription": product_category.family_description,
                        "classCode": product_category.class_code,
                        "classDescription": product_category.class_description,
                        "brickCode": product_category.brick_code,
                        "brickCodeDescription": product_category.brick_code_description
                    }
                    product_category_list.append(product_category_dict)
                    # TODO: add product core attribute
            return_dict['productCategory'] = product_category_list



            for product_media in product_medias:
                if product_media:
                    media_dict = {
                        "id": product_media.id,
                        "type": product_media.get_product_media_type(),
                        "url": product_media.url
                    }
                    if product_media.product_sku_id in product_media_dict.keys():
                        product_media_dict[product_media.product_sku_id].append(media_dict)
                    else:
                        product_media_dict[product_media.product_sku_id] = [media_dict]

            # create a list
            for product_parameter in product_parameters:
                if product_parameter:
                    product_parameters_dict = {
                        "id": product_parameter.id,
                        "name": product_parameter.name,
                        "value": product_parameter.value
                    }
                    if product_parameter.product_sku_id in product_parameter_dict.keys():
                        product_parameter_dict[product_parameter.product_sku_id].append(product_parameters_dict)
                    else:
                        product_parameter_dict[product_parameter.product_sku_id] = [product_parameters_dict]

            product_sku_list = []
            for product_sku in product_skus:
                if product_sku:
                    product_skus_dict = {
                        "id": product_sku.id,
                        "productSku": product_sku.product_sku,
                        "productSkuName": product_sku.product_sku_name,
                        "actionCategory1": product_sku.action_category1,
                        "actionCategory2": product_sku.action_category2,
                        "actionCategory3": product_sku.action_category3,
                        "actionCategory4": product_sku.action_category4,
                        "actionCategory5": product_sku.action_category5,
                        "price": product_sku.price,
                        "vat": product_sku.vat,
                        "currency": product_sku.get_product_sku_currency(),
                        'offeredFrom': product_sku.offered_from,
                        'firstPurchase': product_sku.first_purchase,
                        'lastPurchase': product_sku.last_purchase,
                        'noOfPurchases': product_sku.no_of_purchases,
                        'noOfRefusals': product_sku.no_of_refusals,
                        'noOfViews': product_sku.no_of_views,
                        'averageViewTime': product_sku.average_view_time,
                        'productMedia': check_if_exist(product_media_dict, product_sku.id),
                        'productParameter': check_if_exist(product_parameter_dict, product_sku.id)
                    }
                    product_sku_list.append(product_skus_dict)

            return_dict['productSku'] = product_sku_list
            return_dict['mustNotProducts'] = get_product_sku_sorted(must_not_product_data)
            return_dict['mustProducts'] = get_product_sku_sorted(must_product_data)
            return_dict['wishedProducts'] = get_product_sku_sorted(wished_product_data)
            return_dict['spinOffProducts'] = get_product_sku_sorted(spin_off_product_data)
        except:

            e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
            raise e500
    else:
        e404.data = {'message': 'Product with id {} does not exist in database or you are not authorized to view it'.format(product_id)}
        raise e404

    return return_dict


def put_partner_product(partner_id, product_id, token_auth, product_data):
    '''
    :param partner_id: id of partner
    :param product_id: id of product which will be edited
    :param token_auth: user's autentication token
    :param product_data: edited product data from JSON
    :return: status of edit and data from get_partner_product for this product
    '''
    start_time = time.time()

    login = get_user_login(token_auth)

    if not login:
        raise e401

    # if json product data is empty or corrupted
    if product_data is None:
        e404.data = {'message': 'Error while parsing the json data. Check the json structure'}
        raise e404

    product_dict = {
        "name": None,
        "description": None,
        "lowestPrice": None,
        "highestPrice": None,
        "actualPrice": None,
        "averagePrice": None,
        "vat": None,
        "currency": None,
        "active": None,
        "productMedia": [
            {
                "id": None,
                "type": None,
                "url": None
            }
        ],
        "productParameter": [
            {
                "id": None,
                "name": None,
                "value": None
            }
        ],
        "productSku": [
            {
                "id": None,
                "itemSku": None,
                "itemName": None,
                "actionCategory1": None,
                "actionCategory2": None,
                "actionCategory3": None,
                "actionCategory4": None,
                "actionCategory5": None
            }
        ],
        "mustNotProducts": [
            {
                "id": None
            }
        ],
        "mustProducts": [
            {
                "id": None
            }
        ],
        "wishedProducts": [
            {
                "id": None
            }
        ]
    }

    try: product_dict.update(product_data)
    # if json product data have wrong structure
    except:
        e404.data = {'message': 'Errors while parsing the json data. Check the json structure'}
        raise e404

    product = db.session.query(Product) \
        .join(ProductPartner) \
        .join(Partner) \
        .outerjoin(PartnerUserRel) \
        .filter(PartnerUserRel.matomo_user_id == login) \
        .filter(Partner.uuid == partner_id)\
        .filter(Product.id == product_id)\
        .filter(Product.deleted == False).first()

    if not product:
        e404.data = {'message': 'Product with id {} not found for partner {}'.format(product_id, partner_id)}
        raise e404

    product_media_dict = {}
    product_media_id = []
    product_parameter_dict =  {}
    product_parameter_id = []
    product_sku_dict = {}
    product_sku_id = []
    commit_list = []
    must_not_id = []
    must_id = []
    wished_id = []
    log = []

    try:
        product.name = product_dict['name']
        product.description = product_dict['description']
        product.lowest_price = product_dict['lowestPrice']
        product.highest_price = product_dict['highestPrice']
        product.actual_price = product_dict['actualPrice']
        product.average_price = product_dict['averagePrice']
        product.vat = product_dict['vat']
        product.currency = product_dict['currency']
        product.active = product_dict['active']
    except KeyError:
        log.append({"message":"Product could not be loaded due to KeyError"})

    try:
        for product_media in product_dict['productMedia']:
            if product_media['id']:
                product_media_id.append(product_media['id'])
                product_media_dict[product_media['id']] = product_media
            else:
                try:
                    if product_media['type'] == 'Site' or product_media['type'] == 'YouTube video' or product_media['type'] == 'Picture':
                        commit_list.append(ProductMedia(
                            type = product_media['type'],
                            url = product_media['url'],
                            product_id = product_id
                        ))
                    else:
                        pass
                        #log.append({"message": "{} is not valid Product Media type. Please select Site / Picture / YouTube video".format(product_media['type'])})
                except KeyError:
                    log.append({"message": "New Product Media url {} could not be loaded due to KeyError".format(product_media['url'])})
    except KeyError:
        log.append({"message":"Product Media could not be loaded due to KeyError"})

    product_medias = db.session.query(ProductMedia)\
        .filter(ProductMedia.product_id == product_id)\
        .filter(ProductMedia.id.in_(product_media_id)).all()

    for product_media in product_medias:
        try:
            if product_media_dict[product_media.id]['type'] == 'Site' or product_media_dict[product_media.id]['type'] == 'YouTube video' or product_media_dict[product_media.id]['type'] == 'Picture':
                product_media.type = product_media_dict[product_media.id]['type']
                product_media.url = product_media_dict[product_media.id]['url']
            else:
                log.append({"message": "{} is not valid Product Media type. Please select Site / Picture / YouTube video".format(product_media_dict[product_media.id]['type'])})
        except KeyError:
            log.append({"message": "Product Media id {} could not be loaded due to KeyError".format(product_media.id)})

    try:
        for product_parameter in product_dict['productParameter']:
            if product_parameter['id']:
                product_parameter_id.append(product_parameter['id'])
                product_parameter_dict[product_parameter['id']] = product_parameter
            else:
                try:
                    commit_list.append(ProductParameter(
                        name = product_parameter['name'],
                        value = product_parameter['value'],
                        product_id = product_id
                    ))
                except KeyError:
                    log.append({"message": "New Product Parameter with name {} could not be loaded due to KeyError".format(product_parameter['name'])})
    except KeyError:
        log.append({"message": "Product Parameter could not be loaded due to KeyError"})

    product_parameters = db.session.query(ProductParameter) \
        .filter(ProductParameter.product_id == product_id) \
        .filter(ProductParameter.id.in_(product_parameter_id)).all()

    for product_parameter in product_parameters:
        try:
            product_parameter.name = product_parameter_dict[product_parameter.id]['name']
            product_parameter.value = product_parameter_dict[product_parameter.id]['value']
        except KeyError:
            log.append({"message": "Product Parameter id {} could not be loaded due to KeyError".format(product_parameter.id)})

    try:
        for product_sku in product_dict['productSku']:
            if product_sku['id']:
                product_sku_id.append(product_sku['id'])
                product_sku_dict[product_sku['id']] = product_sku
            else:
                try:
                    commit_list.append(ProductSku(
                        item_sku =  product_sku['itemSku'],
                        item_name =  product_sku['itemName'],
                        action_category1 = product_sku['actionCategory1'],
                        action_category2 = product_sku['actionCategory2'],
                        action_category3 = product_sku['actionCategory3'],
                        action_category4 = product_sku['actionCategory4'],
                        action_category5 = product_sku['actionCategory5'],
                        product_id = product_id
                    ))
                except KeyError:
                    log.append({"message": "New Product Parameter with item name {} could not be loaded due to KeyError".format(product_sku['itemName'])})
    except KeyError:
        log.append({"message": "Product sku could not be loaded due to KeyError"})

    product_skus = db.session.query(ProductSku)\
        .filter(ProductSku.product_id == product_id)\
        .filter(ProductSku.id.in_(product_sku_id)).all()

    for product_sku in product_skus:
        try:
            product_sku.item_sku = product_sku_dict[product_sku.id]['itemSku']
            product_sku.item_name = product_sku_dict[product_sku.id]['itemName']
            product_sku.action_category1 = product_sku_dict[product_sku.id]['actionCategory1']
            product_sku.action_category2 = product_sku_dict[product_sku.id]['actionCategory2']
            product_sku.action_category3 = product_sku_dict[product_sku.id]['actionCategory3']
            product_sku.action_category4 = product_sku_dict[product_sku.id]['actionCategory4']
            product_sku.action_category5 = product_sku_dict[product_sku.id]['actionCategory5']
        except KeyError:
            log.append(
                {"message": "Product Parameter id {} could not be loaded due to KeyError".format(product_sku.id)})

    try:
        must_not_id = list(must_not['id'] for must_not in product_dict['mustNotProducts'])
        db.session.query(MustNotProduct) \
            .filter(MustNotProduct.product_id == product_id) \
            .delete(synchronize_session=False)
        if must_not_id:
            for id in must_not_id:
                commit_list.append(MustNotProduct(
                    product_id=product_id,
                    product_sku_id=id
                ))
    except KeyError:
        log.append({"message": "mustNotProducts could not be loaded due to KeyError"})

    try:
        must_id = list(must['id'] for must in product_dict['mustProducts'])
        db.session.query(MustProduct) \
            .filter(MustProduct.product_id == product_id) \
            .delete(synchronize_session=False)
        if must_id:
            for id in must_id:
                commit_list.append(MustProduct(
                    product_id=product_id,
                    product_sku_id=id
                ))
    except KeyError:
        log.append({"message": "mustProducts could not be loaded due to KeyError"})

    try:
        wished_id = list(wished['id'] for wished in product_dict['wishedProducts'])
        db.session.query(WishedProduct) \
            .filter(WishedProduct.product_id == product_id) \
            .delete(synchronize_session=False)
        if wished_id:
            for id in wished_id:
                commit_list.append(WishedProduct(
                    product_id=product_id,
                    product_sku_id=id
                ))
    except KeyError:
        log.append({"message": "wishedProducts could not be loaded due to KeyError"})

    db.session.bulk_save_objects(commit_list)
    db.session.commit()

    if len(log) < 1:
        errors = {
            "errors":False,
            "messages": []
        }
    else:
        errors = {
            "errors":True,
            "messages": log
        }

    product_dict = get_partner_product(partner_id, product_id, token_auth)
    return_dict = {
        "log": errors,
        "updated": product_dict
    }

    print('total time: ' + str(round(time.time() - start_time, 5)) + ' sec.')
    return return_dict


def delete_partner_product(partner_id, product_id, token_auth):
    '''
    :param partner_id: id of partner
    :param product_id: id of the product which will be deleted
    :param token_auth: user's autentication token
    :return: status of deletion and data from get_partner_product of this product
    '''
    login = get_user_login(token_auth)

    if not login:
        raise e401

    product = db.session.query(Product)\
        .filter_by(id=product_id, active=True) \
        .join(ProductPartner) \
        .join(Partner) \
        .filter(Partner.uuid == partner_id).first()

    if product is None:
        e404.data = {'message': 'Product with id {} does not exist in database or you are not authorized to delete it'.format(product_id)}
        raise e404

    try:
        product_dict = get_partner_product(partner_id, product_id, token_auth)
        return_dict = {
            "deleted": product_dict
        }

        product.active = False

        db.session.commit()

        return return_dict
    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_partner_product_catalog(partner_id, token_auth, limit=100, offset=0):
    def sort_sku(dictionary, sku_data):
        for item in sku_data:
            if not item[0] in dictionary.keys():
                dictionary[item[0]] = [{
                    "id": item[1].id,
                    "productSku": item[1].product_sku,
                    "productSkuName": item[1].product_sku_name,
                    "actionCategory1": item[1].action_category1,
                    "actionCategory2": item[1].action_category2,
                    "actionCategory3": item[1].action_category3,
                    "actionCategory4": item[1].action_category4,
                    "actionCategory5": item[1].action_category5,
                    "price": item[1].price,
                    "vat": item[1].vat,
                    "currency": item[1].get_product_sku_currency(),
                    "offeredFrom": item[1].offered_from,
                    "firstPurchase": item[1].first_purchase,
                    "lastPurchase": item[1].last_purchase,
                    "noOfPurchases": item[1].no_of_purchases,
                    "noOfRefusals": item[1].no_of_refusals,
                    "noOfViews": item[1].no_of_views,
                    "averageViewTime": item[1].average_view_time,
                }]
            else:
                dictionary[item[0]].append({
                    "id": item[1].id,
                    "productSku": item[1].product_sku,
                    "productSkuName": item[1].product_sku_name,
                    "actionCategory1": item[1].action_category1,
                    "actionCategory2": item[1].action_category2,
                    "actionCategory3": item[1].action_category3,
                    "actionCategory4": item[1].action_category4,
                    "actionCategory5": item[1].action_category5,
                    "price": item[1].price,
                    "vat": item[1].vat,
                    "currency": item[1].get_product_sku_currency(),
                    "offeredFrom": item[1].offered_from,
                    "firstPurchase": item[1].first_purchase,
                    "lastPurchase": item[1].last_purchase,
                    "noOfPurchases": item[1].no_of_purchases,
                    "noOfRefusals": item[1].no_of_refusals,
                    "noOfViews": item[1].no_of_views,
                    "averageViewTime": item[1].average_view_time,
                })

    login = get_user_login(token_auth)

    '''
    :param partner_id: id of partner
    :param page: page of product catalog, 100 products per page
    :param token_auth: user's autentication token
    :return: a list of products from database which the partner is authorized to view
    '''

    if not login:
        raise e401

    #start_time = time.time()

    partner_dict = {
        0: []
    }
    core_att_value_dict = {
        0: []
    }
    core_att_dict = {
        0: []
    }
    product_media_dict = {
        0: []
    }
    product_category_dict = {
        0: []
    }
    product_parameters_dict = {
        0: []
    }
    product_sku_dict = {
        0: []
    }
    must_not_dict = {
        0:[]
    }
    must_dict = {
        0: []
    }
    wished_dict = {
        0: []
    }
    spin_off_dict = {
        0: []
    }

    if int(limit) < 1: limit = 100
    if int(offset) < 0: offset = 0

    products = db.session.query(Product) \
    .join(ProductPartner) \
    .join(Partner) \
    .filter(Partner.uuid == partner_id) \
    .filter(Product.active == True) \
    .limit(limit).offset(int(limit) * int(offset)).all()

    if not products:
        e404.data = {'message': 'No products found in database with limit {} and offset {}'.format(limit, offset)}
        raise e404

    try:
        product_ids = list(product.id for product in products)

        # prod
        product_sku = db.session.query(ProductSku) \
            .filter(ProductSku.product_id.in_(product_ids)).all()

        product_sku_ids = list(product_sku.id for product_sku in product_sku)

        # prod
        partner = db.session.query(Product.id, Partner) \
            .join(ProductPartner) \
            .join(Partner) \
            .filter(Product.id.in_(product_ids)).all()

        # prod
        product_category = db.session.query(Product.id, ProductCategory) \
            .join(ProductCategory) \
            .filter(Product.id.in_(product_ids)).all()

        # sku
        product_media = db.session.query(ProductMedia) \
            .filter(ProductMedia.product_sku_id.in_(product_sku_ids)).all()

        # sku
        product_parameter = db.session.query(ProductParameter) \
            .filter(ProductParameter.product_sku_id.in_(product_sku_ids)).all()

        # prod
        product_must = db.session.query(Product.id, ProductSku) \
            .join(MustProduct) \
            .join(ProductSku) \
            .filter(ProductSku.id == MustProduct.product_sku_id)\
            .filter(Product.id.in_(product_ids)).all()

        # prod
        product_must_not = db.session.query(Product.id, ProductSku) \
            .join(MustNotProduct) \
            .join(ProductSku) \
            .filter(ProductSku.id == MustNotProduct.product_sku_id) \
            .filter(Product.id.in_(product_ids)).all()

        # prod
        product_wished = db.session.query(Product.id, ProductSku) \
            .join(WishedProduct) \
            .join(ProductSku) \
            .filter(ProductSku.id == WishedProduct.product_sku_id) \
            .filter(Product.id.in_(product_ids)).all()

        # prod
        product_spin_off = db.session.query(Product.id, ProductSku) \
            .join(SpinOffProduct) \
            .join(ProductSku) \
            .filter(ProductSku.id == SpinOffProduct.product_sku_id) \
            .filter(Product.id.in_(product_ids)).all()

        if product_category:
            product_core_attribute = db.session.query(ProductCoreAttribute)\
                .filter(ProductCoreAttribute.product_category_id.in_(list(id[1].id for id in product_category))).all()

            if product_core_attribute:
                product_core_attribute_value = db.session.query(ProductCoreAttributeValue)\
                    .filter(ProductCoreAttributeValue.product_core_attribute_id.in_(
                            list(id.id for id in product_core_attribute))).all()

                if product_core_attribute_value:
                    for item in product_core_attribute_value:
                        if not item.product_core_attribute_id in core_att_value_dict.keys():
                            core_att_value_dict[item.product_core_attribute_id] = [{
                                "valueCode": item.value_code,
                                "valueDescription": item.value_description
                            }]
                        else:
                            core_att_value_dict[item.product_core_attribute_id].append({
                                "valueCode": item.value_code,
                                "valueDescription": item.value_description
                            })

                for item in product_core_attribute:
                    if not item.product_category_id in core_att_dict.keys():
                        core_att_dict[item.product_category_id] = [{
                            "typeCode": item.type_code,
                            "typeDescription": item.type_description,
                            "productCoreAttributeValue": check_if_exist(core_att_value_dict, item.id)
                        }]
                    else:
                        core_att_dict[item.product_category_id].append({
                            "typeCode": item.type_code,
                            "typeDescription": item.type_description,
                            "productCoreAttributeValue": check_if_exist(core_att_value_dict, item.id)
                        })

        for item in product_category:
            if not item[0] in product_category_dict.keys():
                product_category_dict[item[0]] = [{
                    "id": item[1].id,
                    "segmentCode": item[1].segment_code,
                    "segmentDescription": item[1].segment_description,
                    "familyCode": item[1].family_code,
                    "familyDescription": item[1].family_description,
                    "classCode": item[1].class_code,
                    "classDescription": item[1].class_description,
                    "brickCode": item[1].brick_code,
                    "brickCodeDescription": item[1].brick_code_description,
                    "productCoreAttribute": check_if_exist(core_att_dict, item[1].id)
                }]
            else:
                product_category_dict[item[0]].append({
                    "id": item[1].id,
                    "uuid": item[1].uuid,
                    "name": item[1].name,
                    "description": item[1].description,
                    "type": item[1].partner_type.name
                })

        for item in partner:
            if not item[0] in partner_dict.keys():
                partner_dict[item[0]] = [{
                    "id": item[1].id,
                    "uuid": item[1].uuid,
                    "name": item[1].name,
                    "description": item[1].description,
                    "type": item[1].get_partner_type()
                }]
            else:
                partner_dict[item[0]].append({
                    "id": item[1].id,
                    "uuid": item[1].uuid,
                    "name": item[1].name,
                    "description": item[1].description,
                    "type": item[1].get_partner_type()
                })

        for item in product_media:
            if not item.product_sku_id in product_media_dict.keys():
                product_media_dict[item.product_sku_id] = [{
                    "id": item.id,
                    "type": item.get_product_media_type(),
                    "url": item.url
                }]
            else:
                product_media_dict[item.product_sku_id].append({
                    "id": item.id,
                    "type": item.get_product_media_type(),
                    "url": item.url
                })

        for item in product_parameter:
            if not item.product_sku_id in product_parameters_dict.keys():
                product_parameters_dict[item.product_sku_id] = [{
                    "id": item.id,
                    "name": item.name,
                    "value": item.value
                }]
            else:
                product_parameters_dict[item.product_sku_id].append({
                        "id": item.id,
                        "name": item.name,
                        "value": item.value
                })

        #sort_sku(product_sku_dict, product_sku)

        for item in product_sku:
            if not item.product_id in product_sku_dict.keys():
                product_sku_dict[item.product_id] = [{
                    "id": item.id,
                    "productSku": item.product_sku,
                    "productSkuName": item.product_sku_name,
                    "actionCategory1": item.action_category1,
                    "actionCategory2": item.action_category2,
                    "actionCategory3": item.action_category3,
                    "actionCategory4": item.action_category4,
                    "actionCategory5": item.action_category5,
                    "price": item.price,
                    "vat": item.vat,
                    "currency": item.get_product_sku_currency(),
                    "offeredFrom": item.offered_from,
                    "firstPurchase": item.first_purchase,
                    "lastPurchase": item.last_purchase,
                    "noOfPurchases": item.no_of_purchases,
                    "noOfRefusals": item.no_of_refusals,
                    "noOfViews": item.no_of_views,
                    "averageViewTime": item.average_view_time,
                    "productMedia": check_if_exist(product_media_dict, item.id),
                    "productParameter": check_if_exist(product_parameters_dict, item.id),
                }]
            else:
                product_sku_dict[item.product_id].append({
                    "id": item.id,
                    "productSku": item.product_sku,
                    "productSkuName": item.product_sku_name,
                    "actionCategory1": item.action_category1,
                    "actionCategory2": item.action_category2,
                    "actionCategory3": item.action_category3,
                    "actionCategory4": item.action_category4,
                    "actionCategory5": item.action_category5,
                    "price": item.price,
                    "vat": item.vat,
                    "currency": item.get_product_sku_currency(),
                    "offeredFrom": item.offered_from,
                    "firstPurchase": item.first_purchase,
                    "lastPurchase": item.last_purchase,
                    "noOfPurchases": item.no_of_purchases,
                    "noOfRefusals": item.no_of_refusals,
                    "noOfViews": item.no_of_views,
                    "averageViewTime": item.average_view_time,
                    "productMedia": check_if_exist(product_media_dict, item.id),
                    "productParameter": check_if_exist(product_parameters_dict, item.id),
                })

        sort_sku(must_not_dict, product_must_not)
        sort_sku(must_dict, product_must)
        sort_sku(wished_dict, product_wished)
        sort_sku(spin_off_dict, product_spin_off)

        product_list = []
        for product in products:
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "lowestPrice": product.lowest_price,
                "highestPrice": product.highest_price,
                "averagePrice": product.average_price,
                "vat": product.vat,
                "currency": product.get_product_currency(),
                "offeredFrom": product.offered_from,
                "active": product.active,
                "firstPurchase": product.first_purchase,
                "lastPurchase": product.last_purchase,
                "noOfPurchases": product.no_of_purchases,
                "noOfRefusals": product.no_of_refusals,
                "noOfViews": product.no_of_views,
                "averageViewTime": product.average_view_time,
                "partner": check_if_exist(partner_dict, product.id),
                "productCategory": check_if_exist(product_category_dict, product.id),
                "productSku": check_if_exist(product_sku_dict, product.id),
                "mustNotProducts": check_if_exist(must_not_dict, product.id),
                "mustProducts": check_if_exist(must_dict, product.id),
                "wishedProducts": check_if_exist(wished_dict, product.id),
                "spinOffProducts": check_if_exist(spin_off_dict, product.id)
            }
            product_list.append(product_dict)

        return_dict = {
            "products": product_list
        }
        #print('function took: ' + str(round(time.time() - start_time, 5)) + ' sec.')
        return return_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def post_partner_product_catalog(partner_id, product_data, token_auth):
    '''
    older function for uploading product without [product_must, product_must_not, product_wished, product_spin_off]
    :param partner_id: id of the partner which will be the owner of this product
    :param product_data: data from XML file uploaded on endpoint
    :param token_auth: user's autentication token
    :return: list of product names and their status of database write
    '''

    start_time = time.time()
    return_dict = {
        'success': False,
        'products': 0,
        'productsSku': 0
    }
    prod_name = []
    commit_list = []
    product_dict = {}
    product_sku_dict = {}
    product_parameter_dict = {}
    product_media_dict = {}
    product_geolocation_dict = {}
    must_set = set()
    must_not_set = set()
    wished_set = set()

    def get_data_from_xml(item):

        def load_relationship(item):
            try:
                if item['WISHED_PRODUCT'] is not None or item['MUST_NOT_PRODUCT'] is not None \
                        or item['MUST_PRODUCT'] is not None:

                    if item['WISHED_PRODUCT']:
                        for wished in item['WISHED_PRODUCT']['PRODUCT']:
                            wished_set.add((item['NAME'], wished))

                    if item['MUST_PRODUCT']:
                        for must in item['MUST_PRODUCT']['PRODUCT']:
                            must_set.add((item['NAME'], must))

                    if item['MUST_NOT_PRODUCT']:
                        for must_not in item['MUST_NOT_PRODUCT']['PRODUCT']:
                            must_not_set.add((item['NAME'], must_not))

            except KeyError:
                pass

        def product_category(product_sku):
            try:
                if item['PRODUCT_CATEGORY']:
                    category_list = item['PRODUCT_CATEGORY'].split("|")
                    for i,productCategory in enumerate(category_list):
                        action_cat = 'action_category' + str(i)
                        setattr(product_sku, action_cat, productCategory.strip())
            except KeyError:
                pass

        load_relationship(item)

        if item['NAME'] not in product_dict.keys():
            product_dict[item['NAME']] = Product(
                name=item['NAME'],
                description=item['DESCRIPTION'],
                active=True
            )
            prod_name.append(item['NAME'])

        if item['NAME'] in product_sku_dict.keys():
            product_sku = ProductSku(
                product_sku=item['PRODUCT'],
                product_sku_name=item['PRODUCT_SKU'],
                price=price_check(item['PRICE']))
            product_category(product_sku)
            product_sku_dict[item['NAME']].append(product_sku)
        else:
            product_sku = ProductSku(
                product_sku=item['PRODUCT'],
                product_sku_name=item['PRODUCT_SKU'],
                price=price_check(item['PRICE']))
            product_category(product_sku)
            product_sku_dict[item['NAME']] = [product_sku]

        # parameters, media and geolocation
        # sort geo_locations
        try:
            if type(item['ADDRESSES']['ADDRESS']) == list:
                for geo_location_item in item['ADDRESSES']['ADDRESS']:
                    geo_location = GeoLocation(country=address['COUNTRY'],
                                               street=address['STREET'],
                                               city=address['CITY'],
                                               zip_code=address['ZIP-CODE'],
                                               longitude=address['LONGITUDE'],
                                               latitude=address['LATITUDE'],
                                               geo_location_type=post_type(GEO_LOCATION_TYPE,
                                                                      'product_placement'))
                    if (item['PRODUCT_SKU'], item['PRICE']) in product_geolocation_dict.keys():
                        product_geolocation_dict[(item['PRODUCT_SKU'], item['PRICE'])].append(geo_location)
                    else:
                        product_geolocation_dict[(item['PRODUCT_SKU'], item['PRICE'])] = [geo_location]

            elif item['ADDRESSES']['ADDRESS']:
                geo_location = GeoLocation(country=item['ADDRESSES']['ADDRESS']['COUNTRY'],
                                           street=item['ADDRESSES']['ADDRESS']['STREET'],
                                           city=item['ADDRESSES']['ADDRESS']['CITY'],
                                           zip_code=item['ADDRESSES']['ADDRESS']['ZIP-CODE'],
                                           longitude=item['ADDRESSES']['ADDRESS']['LONGITUDE'],
                                           latitude=item['ADDRESSES']['ADDRESS']['LATITUDE'],
                                           geo_location_type=post_type(GEO_LOCATION_TYPE, 'product_placement'))
                if (item['PRODUCT_SKU'], item['PRICE']) in product_geolocation_dict.keys():
                    product_geolocation_dict[(item['PRODUCT_SKU'], item['PRICE'])].append(geo_location)
                else:
                    product_geolocation_dict[(item['PRODUCT_SKU'], item['PRICE'])] = [geo_location]

        except KeyError:
            pass

        # sort product parameter
        try:
            if type(item['PRODUCT_PARAM']) == list:
                for product_parameter_item in item['PRODUCT_PARAM']:
                    product_parameter = ProductParameter(name=product_parameter_item['PARAM_NAME'],
                                                         value=product_parameter_item['PARAM_VALUE'])
                    if (item['PRODUCT_SKU'], item['PRICE']) in product_parameter_dict.keys():
                        product_parameter_dict[(item['PRODUCT_SKU'], item['PRICE'])].append(product_parameter)
                    else:
                        product_parameter_dict[(item['PRODUCT_SKU'], item['PRICE'])] = [product_parameter]

            elif item['PRODUCT_PARAM']:
                product_parameter = ProductParameter(name=item['PRODUCT_PARAM']['PARAM_NAME'],
                                                     value=item['PRODUCT_PARAM']['PARAM_VALUE'])
                if (item['PRODUCT_SKU'], item['PRICE']) in product_parameter_dict.keys():
                    product_parameter_dict[(item['PRODUCT_SKU'], item['PRICE'])].append(product_parameter)
                else:
                    product_parameter_dict[(item['PRODUCT_SKU'], item['PRICE'])] = [product_parameter]

        except KeyError:
            pass

        # sort product media
        try:
            if type(item['CATALOG_SUBJECT_MEDIA']) == list:
                for product_media_item in item['CATALOG_SUBJECT_MEDIA']:
                    product_media = ProductMedia(type=post_type(MEDIA_TYPE, product_media_item['TYPE']),
                                                 url=product_media_item['URL'])
                    if (item['PRODUCT_SKU'], item['PRICE']) in product_media_dict.keys():
                        product_media_dict[(item['PRODUCT_SKU'], item['PRICE'])].append(product_media)
                    else:
                        product_media_dict[(item['PRODUCT_SKU'], item['PRICE'])] = [product_media]


            elif item['CATALOG_SUBJECT_MEDIA']:
                product_media = ProductMedia(type=post_type(MEDIA_TYPE, item['CATALOG_SUBJECT_MEDIA']['TYPE']),
                                             url=item['CATALOG_SUBJECT_MEDIA']['URL'])
                if (item['PRODUCT_SKU'], item['PRICE']) in product_media_dict.keys():
                    product_media_dict[(item['PRODUCT_SKU'], item['PRICE'])].append(product_media)
                else:
                    product_media_dict[(item['PRODUCT_SKU'], item['PRICE'])] = [product_media]

        except KeyError:
            pass

    def save_products_db():

        def relationship():
            pass

        # prod_name - all unique names of uploading products
        # query the db and return all products that match name with some name from prod_name

        products = db.session.query(Product) \
            .filter(Product.name.in_(prod_name)).all()

        # create a list for existing products
        # product_dict - dictionary with all uploading products
        # pop products that exist in db from product_dict
        # result - products that already exist in existing_products, new products in product_dict
        existing_products = []

        for prod in products:
            if str(prod.name) in product_dict.keys():
                product_dict.pop(str(prod.name), None)
                existing_products.append(prod)

        # not exist - add all skus, commit, query, then add all other tables
        # get the new products from product_dict and upload it to db
        new_products = list(product_dict.values())
        db.session.bulk_save_objects(new_products)
        db.session.commit()

        return_dict['products'] = len(new_products)

        # get the instances of new products
        new_products = db.session.query(Product) \
            .filter(Product.name.in_(list(product.name for product in new_products))).all()

        # new products in new_products
        # existing products in existing_products

        # for new products, match sku, commit to db, retrieve, add all other tables and commit
        # for existing products, match sku, check if they exist in db

        new_products_sku = []
        check_product_sku = []
        check_product_sku_dict = {}

        for product in existing_products:

            if product.name in product_sku_dict.keys():

                for product_sku in product_sku_dict[product.name]:
                    product_sku.product_id = product.id
                    check_product_sku_dict[(str(product_sku.product_sku), int(float(product_sku.price)))] = product_sku

                check_product_sku.extend(product_sku_dict[product.name])
                product_sku_dict.pop(str(product.name), None)

        for product in new_products:

            if product.name in product_sku_dict.keys():

                for product_sku in product_sku_dict[product.name]:
                    product_sku.product_id = product.id

                new_products_sku.extend(product_sku_dict[product.name])
                product_sku_dict.pop(str(product.name), None)

            commit_list.append(ProductPartner(
                product_id=product.id,
                partner_id=partner.id
            ))

        # check product skus
        # commit new product skus

        # print(check_product_sku)
        existing_product_skus = db.session.query(ProductSku) \
            .filter(ProductSku.product_sku.in_(list(sku.product_sku for sku in check_product_sku))) \
            .filter(ProductSku.price.in_(list(sku.price for sku in check_product_sku))).all()

        for product_sku in existing_product_skus:

            if (str(product_sku.product_sku), int(product_sku.price)) in check_product_sku_dict.keys():
                check_product_sku_dict.pop((str(product_sku.product_sku), int(float(product_sku.price))), None)

        new_products_sku.extend(list(check_product_sku_dict.values()))

        db.session.bulk_save_objects(new_products_sku)
        db.session.commit()

        return_dict['productsSku'] = len(new_products_sku)

        # query for the new products_sku and add all other tables
        added_product_skus = db.session.query(ProductSku) \
            .filter(ProductSku.product_sku.in_(list(sku.product_sku for sku in new_products_sku))) \
            .filter(ProductSku.price.in_(list(sku.price for sku in new_products_sku))).all()

        # load others tables that belongs to sku, add sku.id to it and commit

        for product_sku in added_product_skus:

            tpl = (str(product_sku.product_sku_name), str(int(product_sku.price)))

            if tpl in product_geolocation_dict.keys():
                for geo_location in product_geolocation_dict[tpl]:
                    geo_location.product_sku_id = product_sku.id
                    commit_list.append(geo_location)

            if tpl in product_media_dict.keys():
                for media in product_media_dict[tpl]:
                    media.product_sku_id = product_sku.id
                    commit_list.append(media)

            if tpl in product_parameter_dict.keys():
                for parameter in product_parameter_dict[tpl]:
                    parameter.product_sku_id = product_sku.id
                    commit_list.append(parameter)

        db.session.bulk_save_objects(commit_list)
        db.session.commit()

    def save_relationship():

        if len(wished_set) < 1 and len(must_not_set) < 1 and len(must_set) < 1:
            return False

        # wished, must, must not
        relationships = []
        wished_list = []
        if len(wished_set) > 0:

            products = db.session.query(Product)\
                .filter(Product.name.in_(list(item[0] for item in wished_set))).all()
            skus = db.session.query(ProductSku)\
                .filter(ProductSku.product_sku_name.in_(list(item[1] for item in wished_set))).all()

            for item in wished_set:
                relationship = WishedProduct(
                    product_id=get_att_list(products, 'id', 'name', item[0]),
                    product_sku_id=get_att_list(skus, 'id', 'product_sku_name', item[1]),
                )
                if relationship.product_id and relationship.product_sku_id:
                    wished_list.append(relationship)

            # query for existing WishedProduct
            wished_product = db.session.query(WishedProduct)\
                .filter(WishedProduct.product_id.in_(list(wished.product_id for wished in wished_list))) \
                .filter(WishedProduct.product_sku_id.in_(list(wished.product_sku_id for wished in wished_list))).all()

            # remove wished product from wished list that are in wished_product query
            wished_list = delete_lists_duplicates(wished_list, wished_product, 'product_id', 'product_sku_id')

        must_list = []
        if len(must_set) > 0:

            products = db.session.query(Product)\
                .filter(Product.name.in_(list(item[0] for item in must_set))).all()
            skus = db.session.query(ProductSku)\
                .filter(ProductSku.product_sku_name.in_(list(item[1] for item in must_set))).all()

            for item in must_set:
                relationship = MustProduct(
                    product_id=get_att_list(products, 'id', 'name', item[0]),
                    product_sku_id=get_att_list(skus, 'id', 'product_sku_name', item[1]),
                )
                if relationship.product_id and relationship.product_sku_id:
                    must_list.append(relationship)

            # query for existing WishedProduct
            must_product = db.session.query(MustProduct)\
                .filter(MustProduct.product_id.in_(list(must.product_id for must in must_list))) \
                .filter(MustProduct.product_sku_id.in_(list(must.product_sku_id for must in must_list))).all()

            # remove wished product from wished list that are in wished_product query
            must_list = delete_lists_duplicates(must_list, must_product, 'product_id', 'product_sku_id')

        must_not_list = []
        if len(must_not_set) > 0:

            products = db.session.query(Product)\
                .filter(Product.name.in_(list(item[0] for item in must_not_set))).all()
            skus = db.session.query(ProductSku)\
                .filter(ProductSku.product_sku_name.in_(list(item[1] for item in must_not_set))).all()

            for item in must_not_set:
                relationship = MustNotProduct(
                    product_id=get_att_list(products, 'id', 'name', item[0]),
                    product_sku_id=get_att_list(skus, 'id', 'product_sku_name', item[1]),
                )
                if relationship.product_id and relationship.product_sku_id:
                    must_not_list.append(relationship)

            # query for existing WishedProduct
            must_not_product = db.session.query(MustNotProduct)\
                .filter(MustNotProduct.product_id.in_(list(must_not.product_id for must_not in must_not_list))) \
                .filter(MustNotProduct.product_sku_id.in_(list(must_not.product_sku_id for must_not in must_not_list))).all()

            # remove wished product from wished list that are in wished_product query
            must_not_list = delete_lists_duplicates(must_not_list, must_product, 'product_id', 'product_sku_id')

        relationships.extend(wished_list)
        relationships.extend(must_list)
        relationships.extend(must_not_list)
        try:
            db.session.bulk_save_objects(relationships)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            print("Error: {}".format(e))

    if authorize(token_auth):

        if product_data is None:
            e404.data = {'message': 'Xml file is empty or corrupted'}
            raise e404

        #try:
        # get partner
        partner = db.session.query(Partner).filter(Partner.uuid == partner_id).first()

        if not partner:
            e404.data = {'message': 'Partner with id {} does not exist'.format(partner_id)}
            raise e404

        try: product_type = type(product_data['SHOP']['PRODUCT'])
        except KeyError:
            e404.data = {'message': 'XML keys [SHOP][PRODUCT] not found'}
            raise e404

        # multiple products in xml
        if product_type == list:

            for item in product_data['SHOP']['PRODUCT']:
                get_data_from_xml(item)

        else:
            get_data_from_xml(product_data['SHOP']['PRODUCT'])

        print('products: '+str(len(product_dict)))
        print('products sku: ' + str(sum(len(x) for x in product_sku_dict.values())))
        print('parameters: ' + str(sum(len(x) for x in product_parameter_dict.values())))
        #print('parameter keys: '+str(product_parameter_dict.keys()))
        # for x in product_parameter_dict[('SVĚTOVÝ POHÁR V BIATLONU 2018', '0')]:
        #     print(x.name, x.value)
        print('media: ' + str(sum(len(x) for x in product_media_dict.values())))
        print('geolocations: ' + str(sum(len(x) for x in product_geolocation_dict.values())))

        print('must pairs: '+str(len(must_set)))
        print('must not pairs: ' + str(len(must_not_set)))
        print('wished pairs: ' + str(len(wished_set)))

        save_products_db()
        print('saving objects done')
        save_relationship()
        return_dict['success'] = True

        thread = threading.Thread(target=sync_products_attributes, args=())
        thread.daemon = True
        thread.start()

        print('function took: ' + str(round(time.time() - start_time, 5)) + ' sec.')
        return return_dict

        # except:
        #     e404.data = {'message': 'Error while parsing the xml file. Check the file structure'}
        #     raise e404

    else:
        raise e401

    return None


    # products are getting appended to list, then commiting when multiple products are appended
    commit_every = 500
    product_list = []
    sku_set = set()
    product_wished_set = set()
    product_must_set = set()
    product_must_not_set = set()
    product_set = set()
    sku_dict = {}
    #start_time = time.time()

    def product_write_to_database(item, partner):

        def check_if_exists(item):
            for i, product in enumerate(product_list):
                if item['NAME'] == product.name and \
                        item['DESCRIPTION'] == product.description:
                    return True, i
            return False, False

        def check_if_exist_db(item):
            product = db.session.query(Product)\
                .filter(Product.name == item['NAME'])\
                .filter(Product.description == item['DESCRIPTION']).first()

            if product:
                return product
            else:
                return None

        def sort_product_sku(item):
            try: product_sku = ProductSku(product_sku=item['PRODUCT'],
                                          product_sku_name=item['PRODUCT_SKU'],
                                          price=item['PRICE'])
            except KeyError:
                # log that this product sku could not be loaded
                return None

            # sort geo_locations
            try:
                if type(item['ADDRESSES']['ADDRESS']) == list:
                    for geo_location_item in item['ADDRESSES']['ADDRESS']:
                        geo_location = GeoLocation(country=address['COUNTRY'],
                                                   street=address['STREET'],
                                                   city=address['CITY'],
                                                   zip_code=address['ZIP-CODE'],
                                                   longitude=address['LONGITUDE'],
                                                   latitude=address['LATITUDE'])
                        product_sku.geo_location.append(geo_location)

                elif item['ADDRESSES']['ADDRESS']:
                    geo_location = GeoLocation(country=item['ADDRESSES']['ADDRESS']['COUNTRY'],
                                               street=item['ADDRESSES']['ADDRESS']['STREET'],
                                               city=item['ADDRESSES']['ADDRESS']['CITY'],
                                               zip_code=item['ADDRESSES']['ADDRESS']['ZIP-CODE'],
                                               longitude=item['ADDRESSES']['ADDRESS']['LONGITUDE'],
                                               latitude=item['ADDRESSES']['ADDRESS']['LATITUDE'])
                    product_sku.geo_location.append(geo_location)
            except KeyError:
                # log that location could not be loaded
                pass

            # this will take string from product category and split it by " | "
            # so we can assign the stripped strings to actionCategory1, actionCategory2, etc..

            try:
                if item['PRODUCT_CATEGORY']:
                    category_list = item['PRODUCT_CATEGORY'].split("|")
                    for i,productCategory in enumerate(category_list):
                        action_cat = 'action_category' + str(i)
                        setattr(product_sku, action_cat, productCategory.strip())
            except KeyError:
                # log that product categories could not be loaded
                pass

            # sort product media
            try:
                if type(item['CATALOG_SUBJECT_MEDIA']) == list:
                    for product_media_item in item['CATALOG_SUBJECT_MEDIA']:
                        media_type = None
                        if product_media_item['TYPE'].lower() in media_types:
                            media_type = product_media_item['TYPE']
                        product_media = ProductMedia(type=media_type,
                                                     url=product_media_item['URL'])
                        product_sku.product_media.append(product_media)

                elif item['CATALOG_SUBJECT_MEDIA']:
                    media_type = None
                    if item['CATALOG_SUBJECT_MEDIA']['TYPE'].lower() in media_types:
                        media_type = item['CATALOG_SUBJECT_MEDIA']['TYPE']
                    product_media = ProductMedia(type=media_type,
                                                  url=item['CATALOG_SUBJECT_MEDIA']['URL'])
                    product_sku.product_media.append(product_media)

            except KeyError:
                # log that catalog media could not be loaded
                pass

            # sort product parameter
            try:
                if type(item['PRODUCT_PARAM']) == list:
                    for product_parameter_item in item['PRODUCT_PARAM']:
                        product_parameter = ProductParameter(name=product_parameter_item['PARAM_NAME'],
                                                             value=product_parameter_item['PARAM_VALUE'])
                        product_sku.product_parameter.append(product_parameter)

                elif item['PRODUCT_PARAM']:
                    product_parameter = ProductParameter(name=item['PRODUCT_PARAM']['PARAM_NAME'],
                                                         value=item['PRODUCT_PARAM']['PARAM_VALUE'])
                    product_sku.product_parameter.append(product_parameter)

            except KeyError:
                # log that product_parameter could not be loaded
                pass

            return product_sku

        statement, index = check_if_exists(item)

        product = check_if_exist_db(item)

        if not statement and not product: # if product does not exist in product_list
            # sort product
            try:
                product = Product(name=item['NAME'],
                                  description=item['DESCRIPTION'],
                                  active=1)
            except KeyError:
                # log that this product could not be loaded
                print('product sort failed')
                return False


            # sort product_sku
            product_sku = sort_product_sku(item)
            product.product_sku.append(product_sku)

            # add partner to this product
            association_table = ProductPartner()
            association_table.partner = partner
            product.partners.append(association_table)

            # add product to list for commit
            product_list.append(product)

        else: # if product already exist then just add it as product_sku
            # sort product_sku and add it to existing product in list
            product_sku = sort_product_sku(item)
            if product_sku:
                product_list[index].product_sku.append(product_sku)
            else:
                pass
                # log that product_sku could not be loaded

        return True

    def load_relationship(item):
        try:
            if item['WISHED_PRODUCT'] is not None or item['MUST_NOT_PRODUCT'] is not None \
                    or item['MUST_PRODUCT'] is not None:

                if item['WISHED_PRODUCT']:
                    wished_list = list(r for r in item['WISHED_PRODUCT']['PRODUCT'])
                    sku_set.update(wished_list)
                    product_wished_set.add((item['NAME'], item['DESCRIPTION'], *wished_list))
                    product_set.add((item['NAME'], item['DESCRIPTION']))

                if item['MUST_PRODUCT']:
                    must_list = list(r for r in item['MUST_PRODUCT']['PRODUCT'])
                    sku_set.update(must_list)
                    product_must_set.add((item['NAME'], item['DESCRIPTION'], *must_list))
                    product_set.add((item['NAME'], item['DESCRIPTION']))

                if item['MUST_NOT_PRODUCT']:
                    must_not_list = list(r for r in item['MUST_NOT_PRODUCT']['PRODUCT'])
                    sku_set.update(must_list)
                    product_must_not_set.add((item['NAME'], item['DESCRIPTION'], *must_not_list))
                    product_set.add((item['NAME'], item['DESCRIPTION']))

        except KeyError:
            pass

        return True

    def save_relationship():

        def get_id(list, product):
            '''
            :param list: list of products to search in
            :param product: product to search
            :return: id of product if found, or None if not found
            '''
            for item in list:
                if item[0] == product[0] and item[1] == product[1]:
                    return item[2]

        commit_list = []

        # load skus_id
        skus = db.session.query(ProductSku.product_sku_name, ProductSku.id).filter(ProductSku.product_sku_name.in_(sku_set)).all()
        # load products_id
        products = db.session.query(Product.name, Product.description, Product.id). \
            filter(Product.name.in_(r[0] for r in product_set)). \
            filter(Product.description.in_(r[1] for r in product_set)).all()

        # create dictionary from skus_id
        for item in skus: sku_dict[item[0]] = item[1]

        # create all wished relationships
        for product in product_wished_set:
            product_id = get_id(products, product[0:2])

            for wish in product[2:]:
                wished_product = WishedProduct(product_id=product_id, product_sku_id=sku_dict[wish])
                commit_list.append(wished_product)

        # create all must relationships
        for product in product_must_set:
            product_id = get_id(products, product[0:2])

            for wish in product[2:]:
                wished_product = MustProduct(product_id=product_id, product_sku_id=sku_dict[wish])
                commit_list.append(wished_product)

        # create all must_not relationships
        for product in product_must_not_set:
            product_id = get_id(products, product[0:2])

            for wish in product[2:]:
                wished_product = MustNotProduct(product_id=product_id, product_sku_id=sku_dict[wish])
                commit_list.append(wished_product)

        #timer = time.time()
        # add list with relationship objects and commit i
        try:
            db.session.bulk_save_objects(commit_list)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            print("Error: {}".format(e))
        #print('relationship commit took: ' + str(round(time.time() - timer, 5)) + ' sec.')

    if authorize(token_auth):

        if product_data is None:
            e404.data = {'message': 'Xml file is empty or corrupted'}
            raise e404

        # get partner
        partner = db.session.query(Partner).filter(Partner.uuid == partner_id).first()

        if not partner:
            e404.data = {'message': 'Partner with id {} does not exist'.format(partner_id)}
            raise e404

        try: product_type = type(product_data['SHOP']['PRODUCT'])
        except KeyError:
            e404.data = {'message': 'XML keys [SHOP][PRODUCT] not found'}
            raise e404

        # multiple products in xml
        if product_type == list:

            for i,item in enumerate(product_data['SHOP']['PRODUCT']):
                # sort data to commit into models
                product_write_to_database(item, partner)

                # load must / must_not / wished relationships
                load_relationship(item)

                if (i+1) % 50 == 0:
                    break

                # if (i+1) % commit_every == 0:
                #     print('commiting products i: '+str(int((i/commit_every)+1))+'/'+str(int(len(product_data['SHOP']['PRODUCT'])/commit_every)))
                #     l = int(len(product_list)/2)
                #     commit_list, product_list = product_list[:l], product_list[l:]
                #     count_prices(commit_list)
                #     db.session.add_all(commit_list)
                #     db.session.flush()

            return None
            count_prices(product_list)
            db.session.add_all(product_list)
            db.session.commit()
            save_relationship()

        # one product in xml
        else:
            item = product_data['SHOP']['PRODUCT']
            product_write_to_database(item, partner)
            load_relationship(item)

            db.session.add_all(product_list)
            db.session.commit()

            save_relationship()


        return_dict = {
            'status':'successful',
            'products':len(product_data['SHOP']['PRODUCT'])
        }

        #print('function took: ' + str(round(time.time() - start_time, 5)) + ' sec.')
        return return_dict

    else:
        raise e401


def get_partner_product_productsku(partner_id, product_sku_id, token_auth):
    '''
    same as get_partner_product except this one search the product based on product_sku_id
    :param partner_id: id of partner
    :param product_sku_id: id of product_sku
    :param token_auth: user's autentication token
    :return: a dictionary of product which is onwner of searched product_sku
    '''

    if(authorize(token_auth)):

        product_sku = ProductSku.query.filter_by(id=product_sku_id).first()

        if(product_sku):
            product_id = product_sku.product_id
            return get_partner_product(partner_id, product_id, token_auth)

        else:
            e404.data = {'message': 'ProductSku with id {} does not exist in database'.format(product_sku_id)}
            raise e404

    else:
        raise e401


def get_partner_product_statistics(partner_id, product_id, from_date, to_date, token_auth):
    '''
    :param partner_id: id of partner
    :param product_id: id of product which statistics will be returned
    :param token_auth: user's autentication token
    :return: a product_statistics of searched product
    '''

    def sort_tracking_record(tracking_record, dict):
        if tracking_record:
            prod = {
            "id" : tracking_record.id,
            "type" : tracking_record.get_product_tracking_type(),
            "visitorTrackingId" : tracking_record.visitor_tracking_id,
            "productSku" : tracking_record.product_sku,
            "productSkuName" : tracking_record.product_sku_name,
            "price" : tracking_record.price,
            "vat" : tracking_record.vat,
            "orderId" : tracking_record.order_id,
            "timeSpent" : tracking_record.time_spent,
            "searchKey" : tracking_record.search_key,
            "actionCategory1" : tracking_record.action_category1,
            "actionCategory2" : tracking_record.action_category2,
            "actionCategory3" : tracking_record.action_category3,
            "actionCategory4" : tracking_record.action_category4,
            "actionCategory5" : tracking_record.action_category5,
            "timestamp" : tracking_record.timestamp,
            "trackingActionId" : tracking_record.tracking_action_id
            }
            if tracking_record.product_sku_id in dict.keys():
                dict[tracking_record.product_sku_id].append(prod)
            else:
                l = list()
                l.append(prod)
                dict[tracking_record.product_sku_id] = l

    login = get_user_login(token_auth)

    if not login:
        raise e401

    product_data = db.session.query(Product, Partner, ProductCategory, ProductMedia, ProductParameter, ProductSku)\
        .join(ProductPartner)\
        .join(Partner)\
        .filter(Product.id == product_id) \
        .filter(Product.active == True) \
        .filter(Partner.uuid == partner_id) \
        .outerjoin(ProductSku) \
        .outerjoin(ProductCategory) \
        .outerjoin(ProductMedia) \
        .outerjoin(ProductParameter) \
        .all()

    if not product_data:
        e404.data = {'message': 'Product with id {} does not exist in database'\
                                ' or you are not autorized to view it'.format(product_id)}
        raise e404

    try:
        product = list(set(r[0] for r in product_data))
        partners = list(set(r[1] for r in product_data))
        product_categories = list(set(r[2] for r in product_data))
        product_medias = list(set(r[3] for r in product_data))
        product_parameters = list(set(r[4] for r in product_data))
        product_skus = list(set(r[5] for r in product_data))
        product_media_dict = {
            0: []
        }
        product_parameter_dict = {
            0: []
        }
        product_tracking_record_dict = {
            0: []
        }

        product_tracking_records = db.session.query(ProductTrackingRecord)\
            .filter(ProductTrackingRecord.product_sku_id.in_(sku.id for sku in product_skus))\
            .filter(ProductTrackingRecord.timestamp.between(from_date,to_date)).all()

        #print(product_tracking_records)
        #print(len(product_tracking_records))

        if product_tracking_records:
            for product_tracking_record in product_tracking_records:
                sort_tracking_record(product_tracking_record, product_tracking_record_dict)

        return_dict = {
            "id": product[0].id,
            "name": product[0].name,
            "fromTimestamp": from_date,
            "toTimestamp": to_date,
            "description": product[0].description,
            "lowestPrice": product[0].lowest_price,
            "highestPrice": product[0].highest_price,
            "averagePrice": product[0].average_price,
            "vat": product[0].vat,
            "currency": product[0].get_product_currency(),
            'offeredFrom': product[0].offered_from,
            'firstPurchase': product[0].first_purchase,
            'lastPurchase': product[0].last_purchase,
            'noOfPurchases': product[0].no_of_purchases,
            'noOfRefusals': product[0].no_of_refusals,
            'noOfViews': product[0].no_of_views,
            'averageViewTime': product[0].average_view_time
        }

        partner_list = []
        if partners[0] is not None:
            for partner in partners:
                partner_dict = {
                    "id": partner.uuid,
                    "name": partner.name,
                    "description:": partner.description,
                    "type": partner.get_partner_type()
                }
                partner_list.append(partner_dict)
        return_dict['partner'] = partner_list

        product_category_list = []
        if product_categories[0] is not None:
            for product_category in product_categories:
                product_category_dict = {
                    "id": product_category.id,
                    "segmentCode": product_category.segment_code,
                    "segmentDescription": product_category.segment_description,
                    "familyCode": product_category.family_code,
                    "familyDescription": product_category.family_description,
                    "classCode": product_category.class_code,
                    "classDescription": product_category.class_description,
                    "brickCode": product_category.brick_code,
                    "brickCodeDescription": product_category.brick_code_description
                }
                product_category_list.append(product_category_dict)
                # TODO: add product core attribute
        return_dict['productCategory'] = product_category_list

        if product_medias[0] is not None:
            for product_media in product_medias:
                media_dict = {
                    "id": product_media.id,
                    "type": product_media.get_product_media_type(),
                    "url": product_media.url
                }
                if product_media.product_sku_id in product_media_dict.keys():
                    product_media_dict[product_media.product_sku_id].append(media_dict)
                else:
                    product_media_dict[product_media.product_sku_id] = [media_dict]

        # create a list
        if product_parameters[0] is not None:
            for product_parameter in product_parameters:
                product_parameters_dict = {
                    "id": product_parameter.id,
                    "name": product_parameter.name,
                    "value": product_parameter.value
                }
                if product_parameter.product_sku_id in product_parameter_dict.keys():
                    product_parameter_dict[product_parameter.product_sku_id].append(product_parameters_dict)
                else:
                    product_parameter_dict[product_parameter.product_sku_id] = [product_parameters_dict]

        product_sku_list = []
        if product_skus[0] is not None:

            for product_sku in product_skus:
                product_skus_dict = {
                    "id": product_sku.id,
                    "productSku": product_sku.product_sku,
                    "productSkuName": product_sku.product_sku_name,
                    "actionCategory1": product_sku.action_category1,
                    "actionCategory2": product_sku.action_category2,
                    "actionCategory3": product_sku.action_category3,
                    "actionCategory4": product_sku.action_category4,
                    "actionCategory5": product_sku.action_category5,
                    "price": product_sku.price,
                    "vat": product_sku.vat,
                    "currency": product_sku.get_product_sku_currency(),
                    'offeredFrom': product_sku.offered_from,
                    'firstPurchase': product_sku.first_purchase,
                    'lastPurchase': product_sku.last_purchase,
                    'noOfPurchases': product_sku.no_of_purchases,
                    'noOfRefusals': product_sku.no_of_refusals,
                    'noOfViews': product_sku.no_of_views,
                    'averageViewTime': product_sku.average_view_time,
                    'productMedia': check_if_exist(product_media_dict, product_sku.id),
                    'productParameter': check_if_exist(product_parameter_dict, product_sku.id),
                    'productTrackingRecord': check_if_exist(product_tracking_record_dict, product_sku.id)
                }
                product_sku_list.append(product_skus_dict)

        return_dict['productSku'] = product_sku_list

        return return_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def post_partner_product_categories(partner_id, product_categories_data, token_auth):
    '''
    used to upload GS1 product categories
    :param partner_id: id of partner
    :param product_categories_data: product category data
    :param token_auth: user's autentication token
    :return: list of product categories and upload statuses
    '''

    def wr_category(segment_data, family_data, classes_data, brick_data):
        product_category = ProductCategory(segment_code=segment_data['@code'],
                                           segment_description=segment_data['@text'],
                                           family_code = family_data['@code'],
                                           family_description = family_data['@text'],
                                           class_code = classes_data['@code'],
                                           class_description = classes_data['@text'],
                                           brick_code = brick_data['@code'],
                                           brick_code_description = brick_data['@text'])
        return product_category

    if authorize(token_auth):

        if product_categories_data is None:
            e404.data = {'message': 'Xml file is empty or corrupted'}
            raise e404

        i_segment = 0
        i_family = 0
        i_class = 0
        i_brick = 0

        try:
            for segment in product_categories_data['sh:StandardBusinessDocument']['eanucc:message']['gpc:gs1Schema']['schema']['segment']:
                i_segment += 1
                category_list = []

                if(type(segment['family']) == list):
                    for family in segment['family']:
                        i_family += 1

                        if(type(family['class']) == list):
                            for classes in family['class']:
                                i_class += 1

                                if(type(classes['brick']) == list):
                                    for brick in classes['brick']:
                                        i_brick += 1
                                        category_list.append(wr_category(segment, family, classes, brick))

                                else:
                                    i_brick += 1
                                    category_list.append(wr_category(segment, family, classes, classes['brick']))

                        else:
                            i_class += 1
                            classes = family['class']
                            bricktype = type(classes['brick'])
                            if(bricktype == list):
                                for brick in classes['brick']:
                                    i_brick += 1
                                    category_list.append(wr_category(segment, family, classes, brick))

                            else:
                                brick = classes['brick']
                                i_brick += 1
                                category_list.append(wr_category(segment, family, classes, brick))

                else:
                    i_family += 1
                    family = segment['family']
                    classtype = type(family['class'])
                    if(classtype == list):
                        for classes in family['class']:
                            i_class += 1

                            bricktype = type(classes['brick'])
                            if(bricktype == list):
                                for brick in classes['brick']:
                                    i_brick += 1
                                    category_list.append(wr_category(segment, family, classes, brick))

                            else:
                                brick = classes['brick']
                                i_brick += 1
                                category_list.append(wr_category(segment, family, classes, brick))

                    else:
                        i_class += 1
                        classes = family['class']
                        bricktype = type(classes['brick'])
                        if(bricktype == list):
                            for brick in classes['brick']:
                                i_brick += 1
                                category_list.append(wr_category(segment, family, classes, brick))

                        else:
                            brick = classes['brick']
                            i_brick += 1
                            category_list.append(wr_category(segment, family, classes, brick))

                db.session.bulk_save_objects(category_list)
                db.session.commit()

            return_dict = {
                "status":"Successfull",
                "segments":i_segment,
                "families":i_family,
                "classes":i_class,
                "bricks":i_brick
            }
            return return_dict

        except:
            e404.data = {'message': 'Error while parsing the xml file. Check the file structure'}
            raise e404

    else:
        raise e401


def get_partner_product_categories(partner_id, token_auth, limit=100, offset=0):
    '''
    get a list of product categories (100 at one time)
    :param partner_id: id of partner
    :param page: number of page, 1 page contain 100 product categories
    :param token_auth: user's autentication token
    :return: a list of product categories
    '''

    if(authorize(token_auth)):

        product_categories_dict = {
          "id": None,
          "segmentDescription": None,
          "classDescription": None,
          "brickCodeDescription": None
        }
        product_categories_list = []

        if int(limit) < 0: limit = 100
        if int(offset) < 0: offset = 0

        product_categories = db.session.query(ProductCategory)\
            .limit(limit).offset(int(limit) * int(offset)).all()

        if product_categories:

            try:

                for product_category in product_categories:

                    product_category_dict = product_categories_dict
                    product_category_dict = {
                      "id": product_category.id,
                      "segmentDescription": product_category.segment_description,
                      "classDescription": product_category.class_description,
                      "brickCodeDescription": product_category.brick_code_description
                    }
                    product_categories_list.append(product_category_dict)

                return_dict = {
                    "limit":limit,
                    "offset":offset,
                    "productCategories":product_categories_list
                }

                return return_dict

            except:
                e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
                raise e500

        else:
            e404.data = {'message': 'No product categories in database found with limit {} and offset {}'.format(limit, offset)}
            raise e404

    else:
        raise e401


def get_partner_product_category(partner_id, product_category_id, token_auth):
    '''
    get specific product category
    :param partner_id: id of partner
    :param product_category_id: id of product category which data will be returned
    :param token_auth: user's autentication token
    :return: dictionary of product category data
    '''
    def check_if_exist(dictionary, key):
        if key in dictionary.keys():
            return dictionary[key]
        else: return dictionary[0]

    if not (authorize(token_auth)): raise e401

    product_categories_dict = {
        "id": None,
        "segmentCode": None,
        "segmentDescription": None,
        "familyCode": None,
        "familyDescription": None,
        "classCode": None,
        "classDescription": None,
        "brickCode": None,
        "brickCodeDescription": None
    }
    core_att_dict = {
        "typeCode": None,
        "typeDescription": None
    }
    core_att_value_dict = {
        "valueCode": None,
        "valueDescription": None
    }
    core_att_dict = {
        0: None
    }
    core_att_value_dict = {}

    product_category = ProductCategory.query.filter_by(id=product_category_id).first()

    if not product_category:
        e404.data = {'message': 'Product category with id {} does not exist in database'.format(product_category_id)}
        raise e404

    try:

        product_core_attribute = db.session.query(ProductCoreAttribute)\
            .filter_by(product_category_id=product_category.id).all()

        if product_core_attribute:
            product_core_attribute_value = db.session.query(ProductCoreAttributeValue)\
                .filter(ProductCoreAttributeValue.product_core_attribute_id.in_(
                        list(id.id for id in product_core_attribute))).all()

            if product_core_attribute_value:
                for item in product_core_attribute_value:
                    if not item.product_core_attribute_id in core_att_value_dict.keys():
                        core_att_value_dict[item.product_core_attribute_id] = [{
                            "valueCode": item.value_code,
                            "valueDescription": item.value_description
                        }]
                    else:
                        core_att_value_dict[item.product_core_attribute_id].append({
                            "valueCode": item.value_code,
                            "valueDescription": item.value_description
                        })

            for item in product_core_attribute:
                if not item.product_category_id in core_att_dict.keys():
                    core_att_dict[item.product_category_id] = [{
                        "typeCode": item.type_code,
                        "typeDescription": item.type_description,
                        "productCoreAttributeValue": check_if_exist(core_att_value_dict, item.id)
                    }]
                else:
                    core_att_dict[item.product_category_id].append({
                        "typeCode": item.type_code,
                        "typeDescription": item.type_description,
                        "productCoreAttributeValue": check_if_exist(core_att_value_dict, item.id)
                    })

        product_category_dict = {
            "id": product_category.id,
            "segmentCode": product_category.segment_code,
            "segmentDescription": product_category.segment_description,
            "familyCode": product_category.family_code,
            "familyDescription": product_category.family_description,
            "classCode": product_category.class_code,
            "classDescription": product_category.class_description,
            "brickCode": product_category.brick_code,
            "brickCodeDescription": product_category.brick_code_description,
            "productCoreAttribute": check_if_exist(core_att_dict, product_category.id)
        }

        return product_category_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_partner_product_tracking_record(partner_id, product_sku_id, product_tracking_record_id, token_auth):
    login = get_user_login(token_auth)

    if not login:
        raise 401

    try:
        data = db.session.query(ProductSku, ProductTrackingRecord)\
            .join(Product)\
            .join(ProductPartner)\
            .join(Partner)\
            .filter(Partner.uuid == partner_id)\
            .filter(ProductSku.id == product_sku_id)\
            .filter(ProductTrackingRecord.id == product_tracking_record_id).first()

        product_sku = data[0]
        product_tracking_record = data[1]

        if not product_tracking_record:
            e404.data = {'message': 'Product tracking record id {} for product sku id {} not found' \
                .format(product_tracking_record_id, product_sku_id)}
            raise e404

        geo_locations = db.session.query(GeoLocation)\
            .filter(GeoLocation.visit_tracking_id == product_tracking_record.visit_tracking_id).all()
        devices = db.session.query(Device)\
            .filter(Device.visit_tracking_id == product_tracking_record.visit_tracking_id).all()

        geo_location_list = []
        device_list = []

        if geo_locations:
            geo_location_set = set()
            for geo_location in geo_locations:
                geo_location_set.add((
                    geo_location.get_geo_location_type(),
                    geo_location.counts,
                    geo_location.continent,
                    geo_location.continent_code,
                    geo_location.country,
                    geo_location.country_code,
                    geo_location.city,
                    geo_location.street,
                    geo_location.street_no,
                    geo_location.zip_code,
                    geo_location.latitude,
                    geo_location.longitude,
                ))
            for geo_location in geo_location_set:
                geo_location_list.append({
                    "type": geo_location[0],
                    "counts": geo_location[1],
                    "continent": geo_location[2],
                    "continentCode": geo_location[3],
                    "country": geo_location[4],
                    "countryCode": geo_location[5],
                    "city": geo_location[6],
                    "street": geo_location[7],
                    "streetNo": geo_location[8],
                    "zip": geo_location[9],
                    "latitude": geo_location[10],
                    "longitude": geo_location[11],
                })

        if devices:
            device_set = set()
            for device in devices:
                device_set.add((
                    device.name,
                    device.description,
                    device.get_device_type(),
                    device.operating_system,
                    device.browser,
                    device.resolution
                ))
            for device in device_set:
                device_list.append({
                    "name": device[0],
                    "description": device[1],
                    "type": device[2],
                    "operatingSystem": device[3],
                    "browser": device[4],
                    "resolution": device[5]
                })

        product_tracking_record_dict = {
            "id": product_tracking_record.id,
            "productId": product_sku.product_id,
            "visitorId": product_tracking_record.visitor_id,
            "productSkuId": product_tracking_record.product_sku_id,
            "productSku": product_tracking_record.product_sku,
            "productSkuName": product_tracking_record.product_sku_name,
            "timestamp": product_tracking_record.timestamp,
            "price": product_tracking_record.price,
            "vat": product_tracking_record.vat,
            "trackingVisitorId": product_tracking_record.visitor_tracking_id,
            "actionCategory1": product_tracking_record.action_category1,
            "actionCategory2": product_tracking_record.action_category2,
            "actionCategory3": product_tracking_record.action_category3,
            "actionCategory4": product_tracking_record.action_category4,
            "actionCategory5": product_tracking_record.action_category5,
            "trackingActionId": product_tracking_record.tracking_action_id,
            "productOrderId": product_tracking_record.order_id,
            "timeSpent": product_tracking_record.time_spent,
            "searchedKey": product_tracking_record.search_key,
            "productTrackingRecordType": product_tracking_record.get_product_tracking_type(),
            "device": device_list,
            "geoLocation": geo_location_list
        }

        return product_tracking_record_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_partner_visitors(partner_id, search_text, token_auth, limit=100, offset=0):
    '''
    get a list of visitors
    :param partner_id: id of partner
    :param search_text: #TODO: should be able to search the visitors wich search_text
    :param page: number of page of visitors. 1 page contain 100 visitors
    :param token_auth: user's autentication token
    :return: a list of visitors
    '''

    login = get_user_login(token_auth)

    if not login: raise e401

    if int(limit) < 0: limit = 100
    if int(offset) < 0: offset = 0

    partner = db.session.query(Partner)\
        .filter(Partner.uuid == partner_id).first()

    if not partner:
        e404.data = {'message': 'No partner with id {}'.format(partner_id)}
        raise e404

    visitors = db.session.query(Visitor.id) \
        .filter(Visitor.deleted == False)\
        .filter(Visitor.partner_id == partner.id)\
        .limit(limit).offset(int(limit) * int(offset)).all()

    if not visitors:
        e404.data = {'message': 'No visitors found in database with limit {} and offset {}'.format(limit, offset)}
        raise e404

    try:
        micro_segment = db.session.query(MicroSegment)\
            .filter(MicroSegment.visitor_id.in_(list(visitor[0] for visitor in visitors))).all()

        micro_segment_dict = {
            0: None
        }
        if micro_segment:
            for item in micro_segment:
                if not item.id in micro_segment_dict.keys():
                    micro_segment_dict[item.id] = {
                        "id": item.id,
                        "name": item.name,
                        "description": item.description
                    }

        visitor_list = []
        for visitor in visitors:
            visitor_dict = {
                "id":visitor[0],
                "microSegment": check_if_exist(micro_segment_dict, visitor[0])
            }
            visitor_list.append(visitor_dict)

        return_dict = {
            "visitors": visitor_list
        }

        return return_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_partner_visitor(partner_id, visitor_id, token_auth):
    '''
    get a specific visitor
    :param partner_id: id of partner
    :param visitor_id: backend if of visitors which data will be returned
    :param token_auth: user's autentication token
    :return: return a dictionary of visitor data from database
    '''

    login = get_user_login(token_auth)

    if not login:
        raise e401

    partner = db.session.query(Partner)\
        .filter(Partner.uuid == partner_id).first()

    if not partner:
        e404.data = {'message': 'No partner with id {} found'.format(partner_id)}
        raise e404

    visitor = sync_visitor_attributes(visitor_id)
    visitor = db.session.query(Visitor)\
        .join(Partner, Partner.id == Visitor.partner_id)\
        .filter(Partner.uuid == partner_id)\
        .filter(Visitor.id == visitor_id).first()

    if not visitor:
        e404.data = {'message': 'No visitor with id {} found for partner {}'.format(visitor_id, partner_id)}
        raise e404

    try:
        visitor_id = visitor.id
        journey_pattern_dict = {
            "id": None
        }
        journey_pattern_list = []
        micro_segment_dict = {}
        geo_location_list = []
        device_list = []
        ip_address_list = []
        contact_list = []

        tracking_records = db.session.query(VisitorTrackingRecord.visit_tracking_id)\
            .filter(VisitorTrackingRecord.visitor_tracking_id == visitor.visitor_tracking_id).all()
        tracking_ids = list(tracking[0] for tracking in tracking_records)

        geo_locations = db.session.query(GeoLocation)\
            .filter(GeoLocation.visit_tracking_id.in_(tracking_ids)).all()
        devices = db.session.query(Device)\
            .filter(Device.visit_tracking_id.in_(tracking_ids)).all()
        ip_addresses = db.session.query(IPAddress)\
            .filter(IPAddress.visit_tracking_id.in_(tracking_ids)).all()
        contacts = db.session.query(Contact)\
            .filter(Contact.visitor_id == visitor_id).all()
        micro_segment = db.session.query(MicroSegment)\
            .filter(MicroSegment.visitor_id == visitor_id).first()

        if micro_segment:

            # visitor_journeys = db.session.query(VisitorJourney) \
            #     .filter(VisitorJourney.id == micro_segment.id).all()
            #
            # if visitor_journeys:
            #     for visitor_journey in visitor_journeys:
            #         visitor_journey_dict = {
            #             "id": journey_pattern.id
            #         }
            #         journey_pattern_list.append(journey_pattern_dict)
            # "journeyPattern": journey_pattern_list

            micro_segment_dict = {
                "id": micro_segment.id,
                "name": micro_segment.name,
                "description": micro_segment.description,
            }

        if geo_locations:
            geo_location_set = set()
            for geo_location in geo_locations:
                geo_location_set.add((
                    geo_location.get_geo_location_type(),
                    geo_location.counts,
                    geo_location.continent,
                    geo_location.continent_code,
                    geo_location.country,
                    geo_location.country_code,
                    geo_location.city,
                    geo_location.street,
                    geo_location.street_no,
                    geo_location.zip_code,
                    geo_location.latitude,
                    geo_location.longitude,
                ))
            for geo_location in geo_location_set:
                geo_location_list.append({
                    "type": geo_location[0],
                    "counts": geo_location[1],
                    "continent": geo_location[2],
                    "continentCode": geo_location[3],
                    "country": geo_location[4],
                    "countryCode": geo_location[5],
                    "city": geo_location[6],
                    "street": geo_location[7],
                    "streetNo": geo_location[8],
                    "zip": geo_location[9],
                    "latitude": geo_location[10],
                    "longitude": geo_location[11],
                })

        if devices:
            device_set = set()
            for device in devices:
                device_set.add((
                    device.name,
                    device.description,
                    device.get_device_type(),
                    device.operating_system,
                    device.browser,
                    device.resolution
                ))
            for device in device_set:
                device_list.append({
                    "name": device[0],
                    "description": device[1],
                    "type": device[2],
                    "operatingSystem": device[3],
                    "browser": device[4],
                    "resolution": device[5]
                })

        if ip_addresses:
            ip_address_set = set()
            for ip_address in ip_addresses:
                ip_address_set.add((
                    ip_address.ip_address
                ))
            for ip_address in ip_address_set:
                ip_address_list.append({
                    "ipAddress": ip_address
                })

        if contacts:
            for contact in contacts:
                contact_list.append({
                    "contactType": contact.get_contact_type(),
                    "e-mail": contact.email,
                    "phone": contact.phone,
                    "twittter": contact.twitter,
                    "linkedin": contact.linkedin
                })

        get_visitor_dict = {
            "id": visitor.id,
            "trackingVisitorId": visitor.visitor_tracking_id,
            "firstVisit": visitor.first_visit,
            "lastVisit": visitor.last_visit,
            "partnerId": partner_id,
            "hasMoreVisits": visitor.has_more_visits,
            "totalVisits": visitor.total_visits,
            "totalVisitDuration": visitor.total_visit_duration,
            "totalActions": visitor.total_actions,
            "totalOutlinks": visitor.total_outlinks,
            "totalDownloads": visitor.total_downloads,
            "totalSearches": visitor.total_searches,
            "totalPageViews": visitor.total_page_views,
            "totalUniquePageViews": visitor.total_unique_page_views,
            "totalRevisitedPages": visitor.total_revisited_pages,
            "totalPageViewsWithTiming": visitor.total_page_views_with_timing,
            "mostVisitedSiteName": visitor.most_visited_site_name,
            "totalProductPurchases": visitor.total_product_purchases,
            "totalProductRefusals": visitor.total_product_refusals,
            "totalProductViews": visitor.total_product_views,
            "totalProductSearches": visitor.total_product_searches,
            "mostPurchasedProductSkuId": visitor.most_purchased_product_sku_id,
            "mostRefusedProductSkuId": visitor.most_refused_product_sku_id,
            "mostViewedProductSkuId": visitor.most_viewed_product_sku_id,
            "mostSearchedProductSkuId": visitor.most_searched_product_sku_id,
            "lastPurchase": visitor.last_purchase,
            "targeted": visitor.targeted,
            "converted": visitor.converted,
            "totalRevenue": visitor.total_revenue,
            "totalRefusalRevenue": visitor.total_refused_revenue,
            "totalPotentialRevenue": visitor.total_potential_revenue,
            "visitorType": visitor.get_visitor_type(),
            "microSegment": micro_segment_dict,
            "geoLocation": geo_location_list,
            "device": device_list,
            "ipAddress": ip_address_list,
            "contact": contact_list
        }

        return get_visitor_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def put_partner_visitor(partner_id, visitor_id, token_auth, visitor_data):
    '''
    edit data of specific visitor
    :param partner_id: id of partner
    :param visitor_id: id of visitors which data will be edited
    :param token_auth: user's autentication token
    :param visitor_data: edited data of visitor from JSON
    :return: status of edit with dictionary from function get_partner_visitor
    '''
    if authorize(token_auth):

        if visitor_data is None:
            e404.data = {'message': 'Error while parsing the json data. Check the json structure'}
            raise e404

        visitor_dict = {
            "tracking_visitor_id": None,
            "first_visit": None,
            "last_visit": None,
            "microSegment": {
                "id": None,
                "name": None,
                "description": None
            },
            "geoLocation": [
                {
                    "id": None,
                    "type": None,
                    "name": None,
                    "continent": None,
                    "continent_code": None,
                    "country": None,
                    "country_code": None,
                    "city": None,
                    "street": None,
                    "street_no": None,
                    "zip": None,
                    "latitude": None,
                    "longitude": None
                }
            ],
            "device": [
                {
                    "id": None,
                    "name": None,
                    "description": None,
                    "type": None,
                    "operating_system": None,
                    "browser": None,
                    "resolution": None
                }
            ]
        }


        try: visitor_dict.update(visitor_data)
        except:
            e404.data = {'message': 'Error while parsing the json data. Check the json structure'}
            raise e404

        visitor = Visitor.query.filter_by(id=visitor_id, deleted=False).first()

        if visitor:

            #try:

            visitor.tracking_visitor_id = visitor_dict['tracking_visitor_id']
            # visitor.first_visit = visitor_dict['first_visit']
            # visitor.last_visit = visitor_dict['last_visit']

            micro_segment = MicroSegment.query.filter_by(visitor_id=visitor_id).first()
            geo_locations = GeoLocation.query.filter_by(visitor_id=visitor_id).all()
            devices = Device.query.filter_by(visitor_id=visitor_id).all()

            if micro_segment is None:
                micro_segment = MicroSegment()

            if geo_locations is None:
                geo_location = GeoLocation()
                geo_locations.append(geo_location)

            if devices is None:
                device = Device()
                devices.append(device)

            micro_segment.name = visitor_dict['microSegment']['name']
            micro_segment.description = visitor_dict['microSegment']['description']

            visitor.micro_segment.append(micro_segment)

            i = 0
            for geo_location in geo_locations:
                geo_location.type = visitor_dict['geoLocation'][i]['type']
                geo_location.continent = visitor_dict['geoLocation'][i]['continent']
                geo_location.continent_code = visitor_dict['geoLocation'][i]['continentCode']
                geo_location.country = visitor_dict['geoLocation'][i]['country']
                geo_location.country_code = visitor_dict['geoLocation'][i]['countryCode']
                geo_location.city = visitor_dict['geoLocation'][i]['city']
                geo_location.street = visitor_dict['geoLocation'][i]['street']
                geo_location.street_no = visitor_dict['geoLocation'][i]['streetNo']
                geo_location.zip_code = visitor_dict['geoLocation'][i]['zip']
                geo_location.latitude = visitor_dict['geoLocation'][i]['latitude']
                geo_location.longitude = visitor_dict['geoLocation'][i]['longitude']
                visitor.geo_location.append(geo_location)
                i = i + 1

            i = 0
            for device in devices:
                device.name = visitor_dict['device'][i]['name']
                device.description = visitor_dict['device'][i]['description']
                device.type = visitor_dict['device'][i]['type']
                device.operating_system = visitor_dict['device'][i]['operatingSystem']
                device.browser = visitor_dict['device'][i]['browser']
                device.resolution = visitor_dict['device'][i]['resolution']
                visitor.device.append(device)
                i = i + 1

            db.session.commit()
            visitor_dict = get_partner_visitor(partner_id, visitor_id, token_auth)
            return_dict = {
                "updated": visitor_dict
            }

            return return_dict

            #except:
            #    e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
            #    raise e500

        else:
            e404.data = {'message': 'Visitor with id {} does not exist in database'.format(visitor_id)}
            raise e404

    else:
        raise e401


def get_partner_visitor_statistics(partner_id, visitor_id, from_date, to_date, token_auth):

    login = get_user_login(token_auth)

    if not login:
        raise e401

    partner = db.session.query(Partner)\
        .outerjoin(BehaveeSite)\
        .filter(Partner.uuid == partner_id).first()

    if not partner:
        e404.data = {'message': 'No partner with id {}'.format(partner_id)}
        raise e404

    site_ids = list(site.tracking_site_id for site in partner.behavee_site)

    if not site_ids:
        e404.data = {'message': 'Partner with id {} have no sites'.format(partner_id)}
        raise e404

    start_time = time.time()
    tracking_records = db.session.query(VisitorTrackingRecord)\
        .join(Visitor, Visitor.visitor_tracking_id == VisitorTrackingRecord.visitor_tracking_id)\
        .filter(Visitor.id == visitor_id)\
        .filter(VisitorTrackingRecord.from_timestamp.between(from_date, to_date))\
        .all()

    if not tracking_records:
        e404.data = {'message': 'Visitor {} doesnt have any Visitor Tracking Records between {} and {}'.format(visitor_id, from_date, to_date)}
        raise e404

    try:
        ecommerce_trackings = db.session.query(ProductTrackingRecord.id, ProductTrackingRecord.visit_tracking_id)\
            .filter(ProductTrackingRecord.visit_tracking_id.in_( \
            tracking.visit_tracking_id for tracking in tracking_records if tracking.visit_goal_buyer != 0)).all()

        ecommerce_dict = {
            0: None
        }
        for ecommerce_tracking in ecommerce_trackings:
            if ecommerce_tracking[1] in ecommerce_dict.keys():
                ecommerce_dict[ecommerce_tracking[1]].append({
                    "productTrackingRecordId": ecommerce_tracking[0]
                })
            else:
                ecommerce_dict[ecommerce_tracking[1]] = [{
                    "productTrackingRecordId": ecommerce_tracking[0]
                }]

        tracking_list = []

        for tracking_record in tracking_records:
            tracking_list.append({
                "id": tracking_record.id,
                "timestamp": tracking_record.from_timestamp,
                "visitGoalBuyer": tracking_record.visit_goal_buyer,
                "visitGoalConverted": tracking_record.visit_goal_converted,
                "productTrackingRecord": check_if_exist(ecommerce_dict, tracking_record.visit_tracking_id)
            })

        visitor_statistics = {
            "visitorId": visitor_id,
            "trackingVisitorId": tracking_records[0].visitor_tracking_id,
            "fromTimestamp": from_date,
            "toTimestamp": to_date,
            "visitorTrackingRecord": tracking_list
        }


        return visitor_statistics

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_partner_visitor_tracking_record(partner_id, visitor_id, visitor_tracking_record_id, token_auth):
    login = get_user_login(token_auth)

    if not login:
        raise 401

    try:
        visitor_tracking_record = db.session.query(VisitorTrackingRecord) \
            .join(BehaveeSite, BehaveeSite.id == VisitorTrackingRecord.site_id) \
            .join(Partner) \
            .filter(Partner.uuid == partner_id) \
            .filter(VisitorTrackingRecord.id == visitor_tracking_record_id).first()

        if not visitor_tracking_record:
            e404.data = {'message': 'Visitor tracking record id not found'.format(visitor_tracking_record_id)}
            raise e404

        geo_locations = db.session.query(GeoLocation) \
            .filter(GeoLocation.visit_tracking_id == visitor_tracking_record.visit_tracking_id).all()
        devices = db.session.query(Device) \
            .filter(Device.visit_tracking_id == visitor_tracking_record.visit_tracking_id).all()
        ip_addresses = db.session.query(IPAddress)\
            .filter(IPAddress.visit_tracking_id == visitor_tracking_record.visit_tracking_id).all()
        product_tracking_records = db.session.query(ProductTrackingRecord) \
            .filter(ProductTrackingRecord.visit_tracking_id == visitor_tracking_record.visit_tracking_id).all()

        geo_location_list = []
        device_list = []
        product_tracking_record_list = []
        ip_address_list = []
        visitor_journey_list = []

        if geo_locations:
            geo_location_set = set()
            for geo_location in geo_locations:
                geo_location_set.add((
                    geo_location.get_geo_location_type(),
                    geo_location.counts,
                    geo_location.continent,
                    geo_location.continent_code,
                    geo_location.country,
                    geo_location.country_code,
                    geo_location.city,
                    geo_location.street,
                    geo_location.street_no,
                    geo_location.zip_code,
                    geo_location.latitude,
                    geo_location.longitude,
                ))
            for geo_location in geo_location_set:
                geo_location_list.append({
                    "type": geo_location[0],
                    "counts": geo_location[1],
                    "continent": geo_location[2],
                    "continentCode": geo_location[3],
                    "country": geo_location[4],
                    "countryCode": geo_location[5],
                    "city": geo_location[6],
                    "street": geo_location[7],
                    "streetNo": geo_location[8],
                    "zip": geo_location[9],
                    "latitude": geo_location[10],
                    "longitude": geo_location[11],
                })

        if devices:
            device_set = set()
            for device in devices:
                device_set.add((
                    device.name,
                    device.description,
                    device.get_device_type(),
                    device.operating_system,
                    device.browser,
                    device.resolution
                ))
            for device in device_set:
                device_list.append({
                    "name": device[0],
                    "description": device[1],
                    "type": device[2],
                    "operatingSystem": device[3],
                    "browser": device[4],
                    "resolution": device[5]
                })

        if ip_addresses:
            ip_address_set = set()
            for ip_address in ip_addresses:
                ip_address_set.add((
                    ip_address.ip_address
                ))
            for ip_address in ip_address_set:
                ip_address_list.append({
                    "ipAddress": ip_address
                })

        if product_tracking_records:
            for product_tracking_record in product_tracking_records:
                product_tracking_record_list.append({
                    "id": product_tracking_record.id,
                    "productSkuId": product_tracking_record.product_sku_id,
                    "visitorId": visitor_id,
                    "productTrackingRecordType": product_tracking_record.get_product_tracking_type()
                })

        journeys = get_visitor_journey(visitor_tracking_record.visit_tracking_id)
        if journeys:

            journey_list = []
            for journey in journeys:
                journey_list.append(VisitorJourney(
                    id=journey[0],
                    visit_tracking_id=journey[1],
                    timestamp=journey[2],
                    visit_entry_url=journey[4],
                    visit_exit_url=journey[3],
                    interaction_position=journey[5],
                    time_spent=journey[6]
                ))

            if len(journey_list) > 0:
                for journey in journey_list:
                    visitor_journey_list.append({
                        "id": journey.id,
                        "timestamp": journey.timestamp,
                        "visitEntryUrl": journey.visit_entry_url,
                        "visitExitUrl": journey.visit_exit_url,
                        "interactionPosition": journey.interaction_position,
                        "timeSpent": journey.time_spent
                    })

            visitor_journeys = db.session.query(VisitorJourney) \
                .filter(VisitorJourney.id.in_(list(journey.id for journey in journey_list))).all()

            if visitor_journeys:
                journey_list = delete_lists_duplicates(journey_list, visitor_journeys, 'id', 'visit_tracking_id')

            db.session.bulk_save_objects(journey_list)
            db.session.commit()


        visitor_tracking_record_dict = {
            "id": visitor_tracking_record.id,
            "siteId": visitor_tracking_record.site_id,
            "visitorId": visitor_id,
            "fromTimestamp": visitor_tracking_record.from_timestamp,
            "toTimestamp": visitor_tracking_record.to_timestamp,
            "visitTotalTime": visitor_tracking_record.visit_total_time,
            "visitGoalBuyer": visitor_tracking_record.visit_goal_buyer,
            "visitGoalConverted": visitor_tracking_record.visit_goal_converted,
            "visitEntryUrl": visitor_tracking_record.visit_entry_url,
            "visitExitUrl": visitor_tracking_record.visit_exit_url,
            "visitorJourneyCount": visitor_tracking_record.visitor_journey_count,
            "browserName": visitor_tracking_record.browser_name,
            "browserLanguage": visitor_tracking_record.browser_language,
            "browserVersion": visitor_tracking_record.browser_version,
            "browserEngine": visitor_tracking_record.browser_engine,
            "visitorJourney": visitor_journey_list,
            "device": device_list,
            "geoLocation": geo_location_list,
            "ipAddress": ip_address_list,
            "productTrackingRecord": product_tracking_record_list
        }

        return visitor_tracking_record_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def post_sites(token_auth, partner_id, args):
    # if token_auth provided by user is authorized to write to database
    login = get_user_login(token_auth)

    if not login:
        raise e401

    try:
        data = {
            'name': None,  # site
            'main_url': None,  # site
            'exclude_unknown_urls': 1,  # site
            'excluded_ips': [],  # site
            'excluded_parameters': [],  # site
            'excluded_user_agents': [],  # site
            'sitesearch_keyword_parameters': [],  # site
            'sitesearch_category_parameters': [],  # site
            'sitesearch': 1,  # site
            'ecommerce': 1,  # site
            'keep_url_fragments': 0,  # site
            'currency': 'CZK',  # site
            'timezone': 'Europe/Prague',  # site
            'package': 1,
            'start_date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            'type_': 'website',
            'user_login': login,
            'package': 15
        }
        data.update(args)

        package_template_id = data.pop('package')
        package_templates = PackageManager.list_templates(None)

        # change boolean from True/False to 1/0 representation
        for key, value in data.items():
            if value == True:
                data[key] = 1
            elif value == False:
                data[key] = 0

        try:
            r = SitesManager().addSite(app.config['MATOMO_ADMIN_TOKEN'], **data)
        except MatomoError as e:
            print(str(e))
            pass

        else:
            if 'value' in r:
                PackageManager.add(r['value'], package_templates[package_template_id])

                # sync site to backend
                sync_site(r['value'])

        return {'success': True}

    except:
        raise e500


def get_partner_sites(partner_id, search_text, token_auth):
    '''
    get a list of sites of partner
    :param partner_id: id of partner
    :param search_text: # TODO should be able to filter sites with searched text
    :param token_auth: user's autentication token
    :return: a list of sites
    '''
    return_dict = {}
    behavee_site_list = []
    login = get_user_login(token_auth)

    if not login:
        raise e401

    behavee_site = db.session.query(BehaveeSite)\
        .join(Partner)\
        .filter(Partner.uuid == partner_id) \
        .filter(BehaveeSite.deleted == False).all()

    if not behavee_site:
        e404.data = {'message': 'No sites found for partner id {}'.format(partner_id)}
        raise e404

    try:

        for item in behavee_site:
            behavee_site_list.append({
                "id": item.id,
                "trackingSiteId": item.tracking_site_id,
                "siteName": item.site_name,
                "url": item.url,
                "firstView": item.first_view,
                "lastView": item.last_view,
                "noOfViews": item.no_of_views,
                "averageTimeSpent": item.average_time_spent
            })

        return_dict['sitesFound'] = len(behavee_site)
        return_dict['sites'] = behavee_site_list

        return return_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_partner_site(partner_id, site_id, token_auth):
    '''
    return a specific site of partner
    :param partner_id: id of partner
    :param site_id: id of site which data will be returned
    :param token_auth: user's autentication token
    :return: dictionary with site data from database
    '''
    login = get_user_login(token_auth)

    if not login:
        raise e401

    behavee_site = db.session.query(BehaveeSite, Partner)\
        .join(Partner)\
        .filter(Partner.uuid == partner_id) \
        .filter(BehaveeSite.deleted == False)\
        .filter(BehaveeSite.id == site_id).first()

    if not behavee_site:
        e404.data = {'message': 'No site with id {} found for partner id {}'.format(site_id,partner_id)}
        raise e404

    try:
        partner = behavee_site[1]
        behavee_site = behavee_site[0]

        content_categories = db.session.query(ContentCategory)\
            .filter(ContentCategory.behavee_site_id == site_id).all()

        medias = db.session.query(ProductMedia)\
            .filter(ProductMedia.behavee_site_id == site_id).all()

        content_category_list = []
        if content_categories:
            for content in content_categories:
                content_category_list.append({
                    "id" : content.id,
                    "name" : content.name
                })

        medias_list = []
        if medias:
            for media in medias:
                medias_list.append({
                    "id": media.id,
                    "type": media.get_product_media_type(),
                    "url": media.url
                })

        partner_dict = {}
        if partner:
            partner_dict = {
                "id": partner.uuid,
                "name": partner.name,
                "description": partner.description,
                "companyNumber": partner.company_number,
                "vatNumber": partner.vat_number,
            }

        behavee_site_dict = {
            "id": behavee_site.id,
            "siteType": behavee_site.get_behavee_site_type(),
            "siteUrl": behavee_site.url,
            "siteName": behavee_site.site_name,
            "firstView": behavee_site.first_view,
            "lastView": behavee_site.last_view,
            "noOfViews": behavee_site.no_of_views,
            "noOfSearches": behavee_site.no_of_searches,
            "averageTimeSpent": behavee_site.average_time_spent,
            "currency": behavee_site.get_behavee_site_currency(),
            "trackingSiteId": behavee_site.tracking_site_id,
            "contentCategory": content_category_list,
            "media": medias_list,
            "partner": partner_dict
        }

        return behavee_site_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def put_partner_site(partner_id, site_id, token_auth, args):

    # if token_auth provided by user is authorized to write to database
    login = get_user_login(token_auth)

    if not login:
        raise e401

    try:
        data = {
            'name': None,  # site
            'main_url': None,  # site
            'exclude_unknown_urls': 1,  # site
            'excluded_ips': [],  # site
            'excluded_parameters': [],  # site
            'excluded_user_agents': [],  # site
            'sitesearch_keyword_parameters': [],  # site
            'sitesearch_category_parameters': [],  # site
            'sitesearch': 1,  # site
            'ecommerce': 1,  # site
            'keep_url_fragments': 0,  # site
            'currency': 'CZK',  # site
            'timezone': 'Europe/Prague',  # site
            'package': 1,
            'idsite': site_id
        }
        data.update(args)

        package_template_id = data.pop('package')
        package_templates = PackageManager.list_templates(None)

        # change boolean from True/False to 1/0 representation
        for key, value in data.items():
            if value == True:
                data[key] = 1
            elif value == False:
                data[key] = 0

        try:
            r = SitesManager().updateSite(app.config['MATOMO_ADMIN_TOKEN'], **data)
        except MatomoError as e:
            print(str(e))
            return {'error': str(e)}
        else:
            if 'value' in r:
                PackageManager.add(r['value'], package_templates[package_template_id])

                # sync site to backend
                sync_site(r['value'])

        return {'success': True}

    except:
        raise e500


def delete_partner_site(partner_id, site_id, token_auth):
    '''
    delete a specific site of partner
    :param partner_id: id of partner
    :param site_id: id of site which will be deleted
    :param token_auth: user's autentication token
    :return: a deletion status and dictionary from get_partner_site function
    '''
    login = get_user_login(token_auth)

    if not login:
        raise e401

    behavee_site = db.session.query(BehaveeSite)\
        .join(Partner)\
        .filter(Partner.uuid == partner_id) \
        .filter(BehaveeSite.deleted == False)\
        .filter(BehaveeSite.id == site_id).first()

    if not behavee_site:
        e404.data = {'message': 'No site with id {} found for partner id {}'.format(site_id,partner_id)}
        raise e404

    try:

        behavee_site_dict = get_partner_site(partner_id, site_id, token_auth)
        return_dict = {
            "deleted": behavee_site_dict
        }

        behavee_site.deleted = True
        db.session.commit()

        return return_dict

    except:
        e500.data = {'message': 'Error while parsing the database data. Contact the administrator'}
        raise e500


def get_number_visits(time_from, time_to, token_auth):
    '''
    get number of visits & unique visits from all sites filted with from/to time. superuser's token needed
    :param time_from: start time for time interval
    :param time_to: stop time for time inverval
    :param token_auth: superuser's token
    :return: a list of sites, visits & unique visits in given time interval.
    '''
    if(authorize(token_auth)):

        return number_of_visits(token_auth, time_from, time_to)

    else:
        raise e401


def get_partner_number_visits(time_from, time_to, partner_id, token_auth):
    '''
    get a list of visits & unique visits from partner's sites
    :param time_from: start of time interval
    :param time_to: stop of time interval
    :param partner_id: id of partner which
    :param token_auth: user's autentication token
    :return: list of sites, visits & unique visits for given partner
    '''

    if(authorize(token_auth)):

        return partner_number_of_visits(token_auth, partner_id, time_from, time_to)

    else:
        raise e401


def get_partner_offers(partner_id):
    return 'hello world'


def get_partner_offer(partner_id, offer_id):
    return 'hello world, you requested offer {}'.format(offer_id)


def get_partner_products_statistics(auth_token, partner_id, from_date, to_date):

    login = get_user_login(auth_token)

    if not login:
        raise e401

    partner = db.session.query(Partner)\
        .join(BehaveeSite)\
        .filter(Partner.uuid == partner_id).first()

    if not partner:
        e404.data = {'message': 'partner with id {} does not exist'.format(partner_id)}
        raise e404

    #try:
    idsite = list(p.id for p in partner.behavee_site)
    idsite.append(0)

    sales_dict = {
        0: None
    }
    #start_time = time.time()
    if not from_date and not to_date:
        prod_sales = db.session.query(ProductSales)\
            .filter(ProductSales.site_id.in_(idsite))\
            .filter(ProductSales.position == 1).all()
    else:
        prod_sales = db.session.query(ProductSales) \
            .filter(ProductSales.timestamp.between(from_date, to_date)) \
            .filter(ProductSales.site_id.in_(idsite)) \
            .filter(ProductSales.position == 1).all()

    for sale in prod_sales:
        if str(sale.type) == '1':
            sales_dict[(str(sale.type))+':'+str(sale.timestamp)] = {
                'productSkuId': sale.product_sku_id,
                "productSKU": sale.product_sku,
                "productSKUName": sale.product_sku_name,
                "numberOfPurchases": sale.quantity,
                "purchasedValue": sale.value
            }
        if str(sale.type) == '2':
            sales_dict[(str(sale.type))+':'+str(sale.timestamp)] = {
                'productSkuId': sale.product_sku_id,
                "productSKU": sale.product_sku,
                "productSKUName": sale.product_sku_name,
                "numberOfRefusals": sale.quantity,
                "refusedValue": sale.value
            }
        if str(sale.type) == '3':
            sales_dict[(str(sale.type))+':'+str(sale.timestamp)] = {
                'productSkuId': sale.product_sku_id,
                "productSKU": sale.product_sku,
                "productSKUName": sale.product_sku_name,
                "numberOfInBasket": sale.quantity,
                "inBasketValue": sale.value
            }
        if str(sale.type) == '4':
            sales_dict[(str(sale.type))+':'+str(sale.timestamp)] = {
                'productSkuId': sale.product_sku_id,
                "productSKU": sale.product_sku,
                "productSKUName": sale.product_sku_name,
                "numberOfOutBasket": sale.quantity,
                "outBasketValue": sale.value
            }
    #print('function took: ' + str(round(time.time() - start_time, 5)) + ' sec.')

    if from_date and to_date:
        timestamp = 'AND timestamp BETWEEN \''+str(from_date)+'\' AND \''+str(to_date)+'\' '
    else: timestamp = ''

    q = 'SELECT DATE_FORMAT(timestamp, \'%Y-%m-%d\'), ' \
        'SUM(IF(type=1, quantity, 0)), ' \
        'SUM(IF(type=2, quantity, 0)), ' \
        'SUM(IF(type=3, quantity, 0)), ' \
        'SUM(IF(type=4, quantity, 0)), ' \
        'ROUND(SUM(IF(type=1, price, 0)), 2), ' \
        'ROUND(SUM(IF(type=2, price, 0)), 2), ' \
        'ROUND(SUM(IF(type=3, price, 0)), 2), ' \
        'ROUND(SUM(IF(type=4, price, 0)), 2), ' \
        'SUM(quantity) ' \
        'FROM product_tracking_record ' \
        'WHERE site_id IN '+str(tuple(idsite))+' '+str(timestamp)+'' \
        'GROUP BY DATE_FORMAT(timestamp, \'%Y-%m-%d\') '

    data = db.session.execute(q).fetchall()

    product_sales_overview = {}
    return_dict = {
        "fromTimestamp": from_date,
        "toTimestamp": to_date,
    }
    sales_day_list = []

    i = 0
    for row in data:
        i += 1
        sales_day_list.append({
            'day': row[0],
            'dayOrder': i,
            'purchasedProducts': row[1],
            'refusedProducts': row[2],
            'inBasketProducts': row[3],
            'outBasketProducts': row[4],
            'purchasedValue': row[5],
            'refusedValue': row[6],
            'inBasketValue': row[7],
            'outBasketValue': row[8],
            'numberOfBuyers': row[9],
            'topPurchasedProductSKU': check_if_exist(sales_dict, str(1) + ':' + row[0]),
            'topRefusedProductSKU': check_if_exist(sales_dict, str(2) + ':' + row[0]),
            'topInBasketProductSKU': check_if_exist(sales_dict, str(3) + ':' + row[0]),
            'topOutBasketProductSKU': check_if_exist(sales_dict, str(4) + ':' + row[0])
        })


    product_sales_overview['purchasedProducts'] = sum(list(sale['purchasedProducts'] for sale in sales_day_list))
    product_sales_overview['refusedProducts'] = sum(list(sale['refusedProducts'] for sale in sales_day_list))
    product_sales_overview['inBasketProducts'] = sum(list(sale['inBasketProducts'] for sale in sales_day_list))
    product_sales_overview['outBasketProducts'] = sum(list(sale['outBasketProducts'] for sale in sales_day_list))
    product_sales_overview['purchasedValue'] = round(sum(list(sale['purchasedValue'] for sale in sales_day_list)),2)
    product_sales_overview['refusedValue'] = round(sum(list(sale['refusedValue'] for sale in sales_day_list)),2)
    product_sales_overview['inBasketValue'] = round(sum(list(sale['inBasketValue'] for sale in sales_day_list)),2)
    product_sales_overview['outBasketValue'] = round(sum(list(sale['outBasketValue'] for sale in sales_day_list)),2)
    product_sales_overview['numberOfBuyers'] = sum(list(sale['numberOfBuyers'] for sale in sales_day_list))

    number_of_visitors = db.session.query(func.count(VisitorTrackingRecord.id))\
        .filter(VisitorTrackingRecord.site_id.in_(idsite))\
        .filter(VisitorTrackingRecord.to_timestamp.between(from_date, to_date)).first()

    if number_of_visitors[0]:
        product_sales_overview['numberOfVisitors'] = number_of_visitors[0]
    else: product_sales_overview['numberOfVisitors'] = None

    return_dict['productSalesStatistics'] = product_sales_overview
    return_dict['productSalesDaysStatistics'] = sales_day_list
    return return_dict

    # except:
    #     e500.data = {'message': 'Internal server error. Contact the administrator'}
    #     raise e500
