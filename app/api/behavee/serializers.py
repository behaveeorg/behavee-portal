from flask_restplus import fields, Model, marshal_with
from app.api.restplus import api

# partners - get
get_partners_inner = api.model('Partner\'s List', {
    'id': fields.String(readOnly=True,description='partner\'s ID'),
    'name': fields.String(readOnly=True, description='partner\'s name'),
    'description': fields.String(readOnly=True,description='short description of partner'),
    'type': fields.String(readOnly=True,description='partner\'s type (enum)'),
})

get_partners_serializer = api.model('Get Partners', {
    'partners': fields.Nested(get_partners_inner, description='list of found partner\'s'),
})


# partners - post
post_partners_serializer = api.model('Post Partner', {
    'success': fields.Boolean(readOnly=True,description='Boolean representing the success of post api call'),
})

# partner - put
put_partners_serializer = api.model('Put Partner',{
    'success': fields.Boolean(readOnly=True, description='Boolean representing the success of post api call'),
})


# partner - get
get_partner_crm = api.model('Get Partner\'s CRM', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
})

get_partner_market_segment = api.model('Get Partner\'s Martker Segment', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
})

get_partner_geo_location = api.model('Get Partner\'s Geolocation', {
    "id": fields.Integer(readOnly=True,description='geolocation\'s ID'),
    "type": fields.String(readOnly=True,description='geolocation\'s type (enum)'),
    "continent": fields.String(readOnly=True,description=''),
    "continentCode": fields.String,
    "country": fields.String,
    "countryCode": fields.String,
    "city": fields.String,
    "street": fields.String,
    "streetNo": fields.String,
    "zip": fields.String,
    "latitude": fields.Float,
    "longitude": fields.Float,
})

get_partner_serializer = api.model('Get Partner', {
    'id': fields.String(readOnly=True,description='partner\'s ID'),
    'name': fields.String(readOnly=True,description='partner\'s name'),
    'description': fields.String(readOnly=True,description='short description of partner'),
    'companyNumber': fields.String(readOnly=True,description='partner\'s company number'),
    'vatNumber': fields.String(readOnly=True,description='partner\'s vat number'),
    'type': fields.String(readOnly=True,description='partner\'s type (enum)'),
    'crm': fields.Nested(get_partner_crm),
    'marketSegment': fields.Nested(get_partner_market_segment),
    'geoLocation': fields.List(fields.Nested(get_partner_geo_location), description='sadad'),
})


# partner - delete
delete_partner_serializer = api.model('delete partner', {
    'deleted': fields.Nested(get_partner_serializer),
})


# products get
get_products_query = api.model('Product query', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
})

get_products_serializer = api.model('Product List', {
    'products': fields.List(fields.Nested(get_products_query)),
})


# products - post
post_products_serializer = api.model('Products serializer', {
    'success': fields.Boolean,
    'products': fields.Integer,
    'productsSku': fields.Integer,
})


# product - get
get_product_partner = api.model('partners', {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'type': fields.String,
})

get_product_core_attribute_value = api.model('product core attribute value', {
    'valueCode': fields.Integer,
    'valueDescription': fields.String,
})

get_product_core_attribute = api.model('product core attribute', {
    'typeCode': fields.Integer,
    'typeDescription': fields.String,
    'productCoreAttributeValue': fields.List(fields.Nested(get_product_core_attribute_value)),
})

get_product_product_category = api.model('product category', {
    'id': fields.Integer,
    'segmentCode': fields.Integer,
    'segmentDescription': fields.String,
    'familyCode': fields.Integer,
    'familyDescription': fields.String,
    'classCode': fields.Integer,
    'classDescription': fields.String,
    'brickCode': fields.Integer,
    'brickCodeDescription': fields.String,
    #'productCoreAttribute': fields.List(fields.Nested(get_product_core_attribute)),
})

get_product_media = api.model('product media', {
    'id': fields.Integer,
    'type': fields.String,
    'url': fields.String,
})

get_product_parameter = api.model('product parameter', {
    'id': fields.Integer,
    'name': fields.String,
    'value': fields.String,
})

get_product_relationships = api.model('product relationships', {
    'id': fields.Integer,
    'productSku': fields.String,
    'productSkuName': fields.String,
    'actionCategory1': fields.String,
    'actionCategory2': fields.String,
    'actionCategory3': fields.String,
    'actionCategory4': fields.String,
    'actionCategory5': fields.String,
    'price': fields.Float,
    'vat': fields.Integer,
    'currency': fields.String,
    'offeredFrom': fields.String,
    'firstPurchase': fields.String,
    'lastPurchase': fields.String,
    'noOfPurchases': fields.Integer,
    'noOfRefusals': fields.Integer,
    'noOfViews': fields.Integer,
    'averageViewTime': fields.Integer,
})

get_product_sku = api.model('product sku', {
    'id': fields.Integer,
    'productSku': fields.String,
    'productSkuName': fields.String,
    'actionCategory1': fields.String,
    'actionCategory2': fields.String,
    'actionCategory3': fields.String,
    'actionCategory4': fields.String,
    'actionCategory5': fields.String,
    'price': fields.Float,
    'vat': fields.Integer,
    'currency': fields.String,
    'offeredFrom': fields.String,
    'firstPurchase': fields.String,
    'lastPurchase': fields.String,
    'noOfPurchases': fields.Integer,
    'noOfRefusals': fields.Integer,
    'noOfViews': fields.Integer,
    'averageViewTime': fields.Integer,
    'productMedia': fields.List(fields.Nested(get_product_media)),
    'productParameter': fields.List(fields.Nested(get_product_parameter)),
})

get_product_serializer = api.model('product', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'lowestPrice': fields.Float,
    'highestPrice': fields.Float,
    'averagePrice': fields.Float,
    'vat': fields.Integer,
    'currency': fields.String,
    'offeredFrom': fields.String,
    'firstPurchase': fields.String,
    'lastPurchase': fields.String,
    'noOfPurchases': fields.Integer,
    'noOfRefusals': fields.Integer,
    'noOfViews': fields.Integer,
    'averageViewTime': fields.Integer,
    'partner': fields.List(fields.Nested(get_product_partner)),
    'productCategory': fields.List(fields.Nested(get_product_product_category)),
    'productSku': fields.List(fields.Nested(get_product_sku)),
    'mustNotProducts': fields.List(fields.Nested(get_product_relationships)),
    'mustProducts': fields.List(fields.Nested(get_product_relationships)),
    'wishedProducts': fields.List(fields.Nested(get_product_relationships)),
    'spinOffProducts': fields.List(fields.Nested(get_product_relationships)),
})

# delete product
delete_product_serializer = api.model('delete product serializer', {
    'deleted': fields.Nested(get_product_serializer),
})

put_product_error = api.model('put product error', {
    'message': fields.String,
})

put_product_log = api.model('put product log', {
    'errors': fields.Boolean,
    'messages': fields.List(fields.Nested(put_product_error)),
})

# put product
put_product_serializer = api.model('put product serializer', {
    'log': fields.Nested(put_product_log),
    'updated': fields.List(fields.Nested(get_product_serializer)),
})

# product catalog - get
get_product_catalog = api.model('product catalog', {
    'products': fields.List(fields.Nested(get_product_serializer)),
})

# product catalog - post
post_product_catalog = api.model('post product catalog', {
    'success': fields.Boolean,
    'products': fields.Integer,
    'productsSku': fields.Integer,
})

# visitors - get
visitors_micro_segment = api.model('visitors micro segment', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
})

get_visitors = api.model('visitors inner', {
    'id': fields.String,
    'microSegment': fields.Nested(visitors_micro_segment, skip_none=True),
})

get_visitors_serializer = api.model('visitors', {
    'visitors': fields.List(fields.Nested(get_visitors, skip_none=True)),
})


# visitor - get
visitor_journey_pattern = api.model('visitor journey pattern',{
    "id": fields.String,
})

visitor_micro_segment = api.model('visitor micro segment', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'journeyPattern': fields.List(fields.Nested(visitor_journey_pattern))
})

visitor_geo_location = api.model('visitor geo location', {
    "type": fields.String,
    "name": fields.String,
    "continent": fields.String,
    "continentCode": fields.String,
    "country": fields.String,
    "countryCode": fields.String,
    "city": fields.String,
    "street": fields.String,
    "streetNo": fields.String,
    "zip": fields.String,
    "latitude": fields.Float,
    "longitude": fields.Float,
})

visitor_device = api.model('visitor device', {
    'name': fields.String,
    'description': fields.String,
    'type': fields.String,
    'operatingSystem': fields.String,
    'browser': fields.String,
    'resolution': fields.String,
})

visitor_ipaddress = api.model('visitor ip address', {
    'ipAddress': fields.String,
})

visitor_contact = api.model('visitor contact', {
    "contactType": fields.String,
    "e-mail": fields.String,
    "phone": fields.String,
    "twittter": fields.String,
    "linkedin": fields.String,
})

get_visitor_serializer = api.model('visitor inner', {
    "id": fields.Integer,
    "trackingVisitorId": fields.String,
    "firstVisit": fields.String,
    "lastVisit": fields.String,
    "partnerId": fields.String,
    "hasMoreVisits": fields.Integer,
    "totalVisits": fields.Integer,
    "totalVisitDuration": fields.Integer,
    "totalActions": fields.Integer,
    "totalOutlinks": fields.Integer,
    "totalDownloads": fields.Integer,
    "totalSearches": fields.Integer,
    "totalPageViews": fields.Integer,
    "totalUniquePageViews": fields.Integer,
    "totalRevisitedPages": fields.Integer,
    "totalPageViewsWithTiming": fields.Integer,
    "mostVisitedSiteName": fields.String,
    "totalProductPurchases": fields.Integer,
    "totalProductRefusals": fields.Integer,
    "totalProductViews": fields.Integer,
    "totalProductSearches": fields.Integer,
    "mostPurchasedProductSkuId": fields.Integer,
    "mostRefusedProductSkuId": fields.Integer,
    "mostViewedProductSkuId": fields.Integer,
    "mostSearchedProductSkuId": fields.Integer,
    "lastPurchase": fields.String,
    "targeted": fields.Integer,
    "converted": fields.Integer,
    "totalRevenue": fields.Float,
    "totalRefusalRevenue": fields.Float,
    "totalPotentialRevenue": fields.Float,
    "visitorType": fields.String,
    "microSegment": fields.Nested(visitor_micro_segment),
    "geoLocation": fields.List(fields.Nested(visitor_geo_location)),
    "device": fields.List(fields.Nested(visitor_device)),
    "ipAddress": fields.List(fields.Nested(visitor_ipaddress)),
    "contact": fields.List(fields.Nested(visitor_contact)),
})


# visitor put
put_visitor_serializer = api.model('put visitor serializer', {
    'updated': fields.Nested(get_visitor_serializer),
})

# get product category
get_product_category_serializer = api.model('product category id', {
    'id': fields.Integer,
    'segmentCode': fields.Integer,
    'segmentDescription': fields.String,
    'familyCode': fields.Integer,
    'familyDescription': fields.String,
    'classCode': fields.Integer,
    'classDescription': fields.String,
    'brickCode': fields.Integer,
    'brickCodeDescription': fields.String,
    'productCoreAttribute': fields.List(fields.Nested(get_product_core_attribute)),
})

# product statistics - get
get_product_statistics_parameter = api.model('product statisctics parameter', {
    'id': fields.Integer,
    'name': fields.String,
    'value': fields.String,
})

get_product_statistics_category = api.model('product statisctics category', {
    'id': fields.Integer,
    'segmentCode': fields.Integer,
    'segmentDescription': fields.String,
    'familyCode': fields.Integer,
    'familyDescription': fields.String,
    'classCode': fields.Integer,
    'classDescription': fields.String,
    'brickCode': fields.Integer,
    'brickCodeDescription': fields.String,
})

get_product_statistics_purchase = api.model('product statistics purchase', {
    'orderId': fields.Integer,
    'price': fields.Float,
    'trackingActionId': fields.String,
    'visitorId': fields.String,
    'visitorTrackingId': fields.String,
    'itemSku': fields.String,
    'itemName': fields.String,
    'actionCategory1': fields.String,
    'actionCategory2': fields.String,
    'actionCategory3': fields.String,
    'actionCategory4': fields.String,
    'actionCategory5': fields.String,
})

get_product_statistics_refusal = api.model('product statistics refusal', {
    'price': fields.Float,
    'trackingActionId': fields.String,
    'visitorId': fields.String,
    'visitorTrackingId': fields.String,
    'itemSku': fields.String,
    'itemName': fields.String,
    'actionCategory1': fields.String,
    'actionCategory2': fields.String,
    'actionCategory3': fields.String,
    'actionCategory4': fields.String,
    'actionCategory5': fields.String,
})

get_product_statistics_view = api.model('product statistics view', {
    'timeSpent': fields.String,
    'trackingActionId': fields.String,
    'visitorId': fields.String,
    'visitorTrackingId': fields.String,
    'itemSku': fields.String,
    'itemName': fields.String,
    'actionCategory1': fields.String,
    'actionCategory2': fields.String,
    'actionCategory3': fields.String,
    'actionCategory4': fields.String,
    'actionCategory5': fields.String,
})

get_product_statistics_partner = api.model('product statistics partner ', {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'type': fields.String,
})

get_product_statistics_product_tracking_record = api.model('product statistics tracking',{
    "id": fields.Integer,
    "type": fields.String,
    "visitorTrackingId": fields.String,
    "productSku": fields.String,
    "productSkuName": fields.String,
    "price": fields.Float,
    "vat": fields.Integer,
    "orderId": fields.String,
    "timeSpent": fields.Integer,
    "searchKey": fields.String,
    "actionCategory1": fields.String,
    "actionCategory2": fields.String,
    "actionCategory3": fields.String,
    "actionCategory4": fields.String,
    "actionCategory5": fields.String,
    "timestamp": fields.String,
    "trackingActionId": fields.String,
})

get_product_statistics_product_sku = api.model('product statistics - product sku', {
    'id': fields.Integer,
    'productSku': fields.String,
    'productSkuName': fields.String,
    'actionCategory1': fields.String,
    'actionCategory2': fields.String,
    'actionCategory3': fields.String,
    'actionCategory4': fields.String,
    'actionCategory5': fields.String,
    'price': fields.Float,
    'vat': fields.Integer,
    'currency': fields.String,
    'offeredFrom': fields.String,
    'firstPurchase': fields.String,
    'lastPurchase': fields.String,
    'noOfPurchases': fields.Integer,
    'noOfRefusals': fields.Integer,
    'noOfViews': fields.Integer,
    'averageViewTime': fields.Integer,
    'productMedia': fields.List(fields.Nested(get_product_media)),
    'productParameter': fields.List(fields.Nested(get_product_parameter)),
    "productTrackingRecord": fields.List(fields.Nested(get_product_statistics_product_tracking_record)),
})

get_product_statistics = api.model('product statistics', {
    "id": fields.Integer,
    "name": fields.String,
    "fromTimestamp": fields.String,
    "toTimestamp": fields.String,
    "description": fields.String,
    "lowestPrice": fields.Float,
    "highestPrice": fields.Float,
    "averagePrice": fields.Float,
    "vat": fields.Integer,
    "currency": fields.String,
    "offeredFrom": fields.String,
    "firstPurchase": fields.String,
    "lastPurchase": fields.String,
    "noOfPurchases": fields.Integer,
    "noOfRefusals": fields.Integer,
    "noOfViews": fields.Integer,
    "averageViewTime": fields.Integer,
    "partner": fields.List(fields.Nested(get_product_statistics_partner)),
    "productCategory": fields.List(fields.Nested(get_product_category_serializer)),
    "productSku": fields.List(fields.Nested(get_product_statistics_product_sku)),
})


# post product categories
post_product_categories = api.model('post product categories', {
    'status': fields.String,
    'segments': fields.Integer,
    'families': fields.Integer,
    'classes': fields.Integer,
    'bricks': fields.Integer
})


# get product categories
get_product_categories = api.model('product categories', {
    'id': fields.Integer,
    'segmentDescription': fields.String,
    'classDescription': fields.String,
    'brickCodeDescription': fields.String,
})

get_product_categories_serializer = api.model('get product categories serializer', {
    'limit': fields.Integer,
    'offset': fields.Integer,
    'productCategories': fields.List(fields.Nested(get_product_categories)),
})

# get sites
get_sites_inner = api.model('get sites', {
    'id': fields.Integer,
    'trackingSiteId': fields.Integer,
    'siteName': fields.String,
    'url': fields.String,
    'firstView': fields.String,
    'lastView': fields.String,
    'noOfViews': fields.Integer,
    'averageTimeSpent': fields.Integer,
})

get_sites_serializer = api.model('get sites serializer', {
    'sitesFound': fields.Integer,
    'sites': fields.List(fields.Nested(get_sites_inner)),
})

# get site
get_site_partner = api.model('product statistics partner ', {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'companyNumber': fields.String,
    'vatNumber': fields.String,
})

get_site_media = api.model('get site media ', {
    'id': fields.Integer,
    'type': fields.String,
    'url': fields.String,
})

get_site_content = api.model('get site content ', {
    'id': fields.Integer,
    'name': fields.String,
})

get_site_serializer = api.model('get site', {
    'id': fields.Integer,
    'siteName': fields.String,
    'siteUrl': fields.String,
    'firstView': fields.String,
    'lastView': fields.String,
    'noOfViews': fields.Integer,
    'noOfSearches': fields.Integer,
    'averageTimeSpent': fields.Integer,
    'currency': fields.String,
    'trackingSiteId': fields.Integer,
    'contentCategory': fields.List(fields.Nested(get_site_content)),
    'media': fields.List(fields.Nested(get_site_media)),
    'partner': fields.Nested(get_site_partner),
})

# site put
put_site_serializer = api.model('Put Site', {
    'success': fields.Boolean,
})

# site delete
delete_site_serializer = api.model('delete sites serializer', {
    'deleted': fields.Nested(get_site_serializer),
})

# get partner product statistics
get_partner_product_statistics_sales = api.model('partner product statistics sales', {
	"purchasedProducts": fields.Integer,
	"refusedProducts": fields.Integer,
	"inBasketProducts": fields.Integer,
	"outBasketProducts": fields.Integer,
	"purchasedValue": fields.Float,
	"refusedValue": fields.Float,
	"inBasketValue": fields.Float,
	"outBasketValue": fields.Float,
	"numberOfBuyers": fields.Integer,
	"numberOfVisitors": fields.Integer,
})

get_partner_product_statistics_purchased = api.model('product statistics purchased', {
    "id": fields.Integer,
    "productSKU": fields.String,
    "productSKUName": fields.String,
    "numberOfPurchases": fields.Integer,
    "purchasedValue": fields.Float,
})

get_partner_product_statistics_refused = api.model('product statistics refused', {
    "id": fields.Integer,
    "productSKU": fields.String,
    "productSKUName": fields.String,
    "numberOfRefusals": fields.Integer,
    "refusedValue": fields.Float,
})

get_partner_product_statistics_in_basket = api.model('product statistics in basket', {
    "id": fields.Integer,
    "productSKU": fields.String,
    "productSKUName": fields.String,
    "numberOfInBasket": fields.Integer,
    "inBasketValue": fields.Float,
})

get_partner_product_statistics_out_basket = api.model('product statistics out basket', {
    "id": fields.Integer,
    "productSKU": fields.String,
    "productSKUName": fields.String,
    "numberOfOutBasket": fields.Integer,
    "outBasketValue": fields.Float,
})

get_partner_product_statistics_day_sales = api.model('product statistics day sales', {
    "day": fields.String,
    "dayOrder": fields.Integer,
    "purchasedProducts": fields.Integer,
    "refusedProducts": fields.Integer,
    "inBasketProducts": fields.Integer,
    "outBasketProducts": fields.Integer,
    "purchasedValue": fields.Float,
    "refusedValue": fields.Float,
    "inBasketValue": fields.Float,
    "outBasketValue": fields.Float,
    "numberOfBuyers": fields.Integer,
    "topPurchasedProductSKU": fields.Nested(get_partner_product_statistics_purchased,skip_none=True),
    "topRefusedProductSKU": fields.Nested(get_partner_product_statistics_refused,skip_none=True),
    "topInBasketProductSKU": fields.Nested(get_partner_product_statistics_in_basket,skip_none=True),
    "topOutBasketProductSKU": fields.Nested(get_partner_product_statistics_out_basket,skip_none=True)
})

get_partner_products_statistics_serializer = api.model('partner product statistics', {
    "fromTimestamp": fields.String,
    "toTimestamp": fields.String,
    "productSalesStatistics": fields.Nested(get_partner_product_statistics_sales, skip_none=True),
    "productSalesDaysStatistics": fields.List(fields.Nested(get_partner_product_statistics_day_sales))
})

# get Visitor Statistics
get_visitor_statistics_product_category = api.model('Product category', {
    "id": fields.String,
    "familyDescription": fields.String,
    "brickCodeDescription": fields.String
})

get_visitor_statistics_product_search = api.model('Product search', {
    "searchedKey": fields.String,
    "id": fields.String,
    "productId": fields.String,
    "productName": fields.String,
    "productSKU": fields.String,
    "price": fields.Float,
    "priceVat": fields.Float,
    'productCategory': fields.List(fields.Nested(get_visitor_statistics_product_category))
})

get_visitor_statistics_product_view = api.model('Product view', {
    "id": fields.String,
    "productId": fields.String,
    "productName": fields.String,
    "productSKU": fields.String,
    "timeSpent": fields.String,
    'productCategory': fields.List(fields.Nested(get_visitor_statistics_product_category))
})

get_visitor_statistics_product_purchase = api.model('Product purchase', {
    "productId": fields.String,
    "itemName": fields.String,
    "itemSKU": fields.String,
    "orderId": fields.String,
    "price": fields.Float,
    "priceVat": fields.Float,
    "totalValue": fields.Float,
    "totalValueVat": fields.Float,
    'productCategory': fields.List(fields.Nested(get_visitor_statistics_product_category))
})

get_visitor_statistics_product_refusal = api.model('Product refusal', {
    "productId": fields.String,
    "itemName": fields.String,
    "itemSKU": fields.String,
    "price": fields.Float,
    "priceVat": fields.Float,
    "totalValue": fields.Float,
    "totalValueVat": fields.Float,
    'productCategory': fields.List(fields.Nested(get_visitor_statistics_product_category))
})

action_details_search = api.model('actionDetailsSearch', {
    "idpageview": fields.String,
    "serverTimePretty": fields.String,
    "timeSpent": fields.Integer,
    "siteSearchKeyword": fields.String,
    "interactionPosition": fields.Integer,
    "timestamp": fields.String,
    "bandwidth_pretty": fields.String
})

action_details_action = api.model('actionDetailsAction', {
    "url": fields.String,
    "pageTitle": fields.String,
    "idpageview": fields.String,
    "timeSpent": fields.Integer,
    "interactionPosition": fields.Integer,
    "timestamp": fields.String,
    "bandwidth_pretty": fields.String
})

item_details = api.model('itemDetails', {
    "itemSKU": fields.String,
    "itemName": fields.String,
    "price": fields.Float,
    "quantity": fields.Integer
})

action_details_ecommerce_order = api.model('actionDetailsEcommerceOrder', {
    "orderId": fields.String,
    "revenue": fields.Float,
    "revenueSubTotal": fields.Float,
    "revenueTax": fields.Float,
    "revenueShipping": fields.Float,
    "revenueDiscount": fields.Float,
    "items": fields.Integer,
    "timestamp": fields.String,
    'itemDetails': fields.Nested(item_details)
})

action_details_abandoned_cart = api.model('actionDetailsEcommerceOrder', {
    "revenue": fields.Integer,
    "items": fields.Integer,
    "timestamp": fields.String,
    'itemDetails': fields.Nested(item_details)
})

get_visitor_statistics_visit_serializer = api.model('product statistics', {
    'idSite': fields.Integer,
    'idVisit': fields.Integer,
    'visitIp': fields.String,
    'visitorId': fields.String,
    'goalConversions': fields.Integer,
    "firstActionTimestamp": fields.String,
    "lastActionTimestamp": fields.String,
    "siteName": fields.String,
    "visitorType": fields.Integer,
    "visitCount": fields.Integer,
    "daysSinceFirstVisit": fields.Integer,
    "daysSinceLastEcommerceOrder": fields.Integer,
    "visitDuration": fields.Integer,
    "visitDurationPretty": fields.Integer,
    "searches": fields.Integer,
    "actions": fields.Integer,
    "interactions": fields.Integer,
    "referrerType": fields.Integer,
    "referrerTypeName": fields.String,
    "referrerUrl": fields.String,
    "language": fields.String,
    "deviceType": fields.String,
    "deviceBrand": fields.String,
    "deviceModel": fields.String,
    "operatingSystem": fields.String,
    "operatingSystemName": fields.String,
    "operatingSystemVersion": fields.String,
    "browser": fields.String,
    "browserName": fields.String,
    "browserVersion": fields.String,
    "totalEcommerceRevenue": fields.Float,
    "totalEcommerceConversions": fields.Float,
    "totalEcommerceItems": fields.Integer,
    "totalAbandonedCartsRevenue": fields.Float,
    "totalAbandonedCarts": fields.Integer,
    "totalAbandonedCartsItems": fields.Integer,
    "events": fields.Integer,
    "country": fields.String,
    "region": fields.String,
    "city": fields.String,
    "location": fields.String,
    "latitude": fields.Float,
    "longitude": fields.Float,
    "visitLocalTime": fields.String,
    "daysSinceLastVisit": fields.Integer,
    "customVariables": fields.String,
    "resolution": fields.String,
    "providerName": fields.String,
    "providerUrl": fields.String,
    "actionDetailsEcommerceOrder": fields.List(fields.Nested(action_details_ecommerce_order)),
    "actionDetailsAbandonedCart": fields.List(fields.Nested(action_details_ecommerce_order)),
    "actionDetailsAction": fields.List(fields.Nested(action_details_action)),
    "actionDetailsSearch": fields.List(fields.Nested(action_details_search))
})

get_visitor_statistics_product_tracking_record = api.model('product tracking record', {
    "productTrackingRecordId": fields.Integer,
})

get_visitor_statistics_visitor_tracking_record = api.model('visitor statistics tracking',{
    "id": fields.Integer,
    "timestamp": fields.String,
    "visitGoalBuyer": fields.Integer,
    "visitGoalConverted": fields.Integer,
    "productTrackingRecord": fields.List(fields.Nested(get_visitor_statistics_product_tracking_record))
})

get_visitors_statistics_serializer = api.model('visitors statistics', {
    "visitorId": fields.Integer,
    "trackingVisitorId": fields.String,
    "fromTimestamp": fields.String,
    "toTimestamp": fields.String,
    "visitorTrackingRecord": fields.List(fields.Nested(get_visitor_statistics_visitor_tracking_record))
})

get_visitor_tracking_record_device = api.model('tracking record device', {
    "name": fields.String,
    "description": fields.String,
    "type": fields.String,
    "operatingSystem": fields.String,
    "browser": fields.String,
    "resolution": fields.String,
})

get_visitor_tracking_record_geolocation = api.model('tracking record geolocation', {
    "type": fields.String,
    "counts": fields.Integer,
    "continent": fields.String,
    "continentCode": fields.String,
    "country": fields.String,
    "countryCode": fields.String,
    "city": fields.String,
    "street": fields.String,
    "streetNo": fields.String,
    "zip": fields.String,
    "latitude": fields.Float,
    "longitude": fields.Float,
})

get_visitor_tracking_record_ipaddress = api.model('tracking record ipaddress', {
    "ipAddress": fields.String,
})

get_visitor_tracking_record_product_tracking = api.model('tracking record - product', {
	"id": fields.Integer,
    "productSkuId": fields.Integer,
    "visitorId": fields.Integer,
	"productTrackingRecordType": fields.String,
})

get_visitor_tracking_journey = api.model('tracking record - journey', {
	"id": fields.Integer,
	"timestamp": fields.String,
	"visitEntryUrl": fields.String,
	"visitExitUrl": fields.String,
	"interactionPosition": fields.Integer,
	"timeSpent": fields.Integer,
})

get_visitor_tracking_record_serializer = api.model('visitor tracking record', {
    "id": fields.Integer,
    "siteId": fields.Integer,
    "visitorId": fields.Integer,
    "fromTimestamp": fields.String,
    "toTimestamp": fields.String,
    "visitTotalTime": fields.Integer,
    "visitGoalBuyer": fields.Integer,
    "visitGoalConverted": fields.Integer,
    "visitEntryUrl": fields.String,
    "visitExitUrl": fields.String,
    "visitorJourneyCount": fields.Integer,
    "browserName": fields.String,
    "browserLanguage": fields.String,
    "browserVersion": fields.String,
    "browserEngine": fields.String,
    'visitorJourney': fields.List(fields.Nested(get_visitor_tracking_journey)),
    'device': fields.List(fields.Nested(get_visitor_tracking_record_device)),
    'geoLocation': fields.List(fields.Nested(get_visitor_tracking_record_geolocation)),
    'ipAddress': fields.List(fields.Nested(get_visitor_tracking_record_ipaddress)),
    'productTrackingRecord': fields.List(fields.Nested(get_visitor_tracking_record_product_tracking))
})

get_product_tracking_record_serializer = api.model('product tracking record ', {
    "id": fields.Integer,
    "productId": fields.Integer,
    "visitorId": fields.Integer,
    "productSkuId": fields.Integer,
    "productSku": fields.String,
    "productSkuName": fields.String,
    "timestamp": fields.String,
    "price": fields.Integer,
    "vat": fields.Integer,
    "trackingVisitorId": fields.String,
    "actionCategory1": fields.String,
    "actionCategory2": fields.String,
    "actionCategory3": fields.String,
    "actionCategory4": fields.String,
    "actionCategory5": fields.String,
    "trackingActionId": fields.String,
    "productOrderId": fields.String,
    "timeSpent": fields.Integer,
    "searchedKey": fields.String,
    "productTrackingRecordType": fields.String,
    'device': fields.List(fields.Nested(get_visitor_tracking_record_device)),
    'geoLocation': fields.List(fields.Nested(get_visitor_tracking_record_geolocation))
})
