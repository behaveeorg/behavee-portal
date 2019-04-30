from datetime import datetime
from typing import Union
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4

from app import db
from app.constants import ContentType, PartnerType, MediaType, GeoLocationType, DeviceType, ContactType, VisitorType, \
ProductTrackingRecordType, Languages, RoleType, WebsiteCurrency, SiteType
from app.api.behavee.toolbox import get_type, post_type
from app.constants import media_types, PARTNER_TYPE, DEVICE_TYPE, LANGUAGES, VISITOR_TYPE, GEO_LOCATION_TYPE, \
    CONTENT_TYPE, MEDIA_TYPE, CONTACT_TYPE, SITE_TYPE, CURRENCY, PRODUCT_TRACKING_TYPE, ROLE_TYPE, COUNTRY_CODES

class BehaveeSynchronizer(db.Model):
    __tablename__ = 'behavee_synchronizer'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    last_visitor_synchronization = db.Column(db.DateTime, default=datetime(2018, 1, 1,0,0,0))
    last_site_synchronization = db.Column(db.DateTime, default='2018-01-01 00:00:00')
    last_product_synchronization = db.Column(db.DateTime, default='2018-01-01 00:00:00')
    last_partner_synchronization = db.Column(db.DateTime, default='2018-01-01 00:00:00')
    last_user_synchronization = db.Column(db.DateTime, default='2018-01-01 00:00:00')
    last_product_sales_synchronization = db.Column(db.Date, default=datetime(2018, 1, 1,0,0,0))
    site_id = db.Column(db.Integer)
    partner_id = db.Column(db.Integer)

    def __repr__(self):
        return '%r' % self.id


class ReferrerDirect(db.Model):
    __tablename__ = 'referrer_direct'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))

    def __repr__(self):
        return '%r' % self.id


class ReferrerSearchEngine(db.Model):
    __tablename__ = 'referrer_search_engine'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    keyword = db.Column(db.String(255))
    url = db.Column(db.String(255))
    referrer_engine_url = db.Column(db.String(255))

    def __repr__(self):
        return '%r' % self.id


class Product(db.Model):
    """
    Main Behavee model class providing data from Matomo tracking BBrain and Backend for behavee product API.
    """
    __tablename__ = 'product'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    description = db.Column(db.String(1023))
    lowest_price = db.Column(db.Float)
    highest_price = db.Column(db.Float)
    average_price = db.Column(db.Float)
    vat = db.Column(db.Integer)
    currency = db.Column(db.Integer)
    offered_from = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=False)
    first_purchase = db.Column(db.DateTime)
    last_purchase = db.Column(db.DateTime)
    no_of_purchases = db.Column(db.Integer)
    no_of_refusals = db.Column(db.Integer)
    no_of_views = db.Column(db.Integer)
    no_of_searches = db.Column(db.Integer)
    average_view_time = db.Column(db.Integer)
    partners = db.relationship('ProductPartner', backref='Product_Partner')
    must_not_products = db.relationship('MustNotProduct', backref='MustNot_Product')
    must_product = db.relationship('MustProduct', backref='Must_Product')
    wished_product = db.relationship('WishedProduct', backref='Wished_Product')
    spin_off_product = db.relationship('SpinOffProduct', backref='SpinOff_Product')
    product_category = db.relationship('ProductCategory', backref='Product_ProductCategory')
    product_sku = db.relationship('ProductSku', backref='Product_ProductSku')
    product_history = db.relationship('ProductHistory', backref='Product_ProductHistory')
    offer = db.relationship('ProductOffer', backref='Product_ProductOffer')
    basket_offer = db.relationship('ProductBasketOffer', backref='Product_ProductBasketOffer')

    def __repr__(self):
        return '%r' % self.name

    def get_product_currency(self):
        return get_type(CURRENCY, self.currency)

    def post_partner_type(self, enum):
        self.currency = post_type(CURRENCY, enum)
        return True


class ProductSku(db.Model):
    __tablename__ = 'product_sku'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    product_sku = db.Column(db.String(255), index=True)
    product_sku_name = db.Column(db.String(1023))
    action_category1 = db.Column(db.String(255))
    action_category2 = db.Column(db.String(255))
    action_category3 = db.Column(db.String(255))
    action_category4 = db.Column(db.String(255))
    action_category5 = db.Column(db.String(255))
    item_description = db.Column(db.String(255))
    price = db.Column(db.Float, index=True)
    vat = db.Column(db.Integer)
    currency = db.Column(db.Integer)
    offered_from = db.Column(db.DateTime)
    first_purchase = db.Column(db.DateTime)
    last_purchase = db.Column(db.DateTime)
    no_of_purchases = db.Column(db.Integer)
    no_of_refusals = db.Column(db.Integer)
    no_of_views = db.Column(db.Integer)
    no_of_searches = db.Column(db.Integer)
    average_view_time = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    geo_location = db.relationship('GeoLocation', backref='ProductSku_GeoLocation')
    must_not_products = db.relationship('MustNotProduct', backref='MustNot_ProductSku')
    must_product = db.relationship('MustProduct', backref='Must_ProductSku')
    wished_product = db.relationship('WishedProduct', backref='Wished_ProductSku')
    spin_off_product = db.relationship('SpinOffProduct', backref='SpinOff_ProductSku')
    product_parameter = db.relationship('ProductParameter', backref='ProductSku_ProductParameter')
    product_media = db.relationship('ProductMedia', backref='ProductSku_ProductMedia')
    product_tracking_record = db.relationship('ProductTrackingRecord', backref='ProductSku_ProductTrackingRecord')

    def __repr__(self):
        return '%r' % self.product_sku

    def get_product_sku_currency(self):
        return get_type(CURRENCY, self.currency)

    def post_product_sku_currency(self, enum):
        self.currency = post_type(CURRENCY, enum)
        return True


class Partner(db.Model):
    """
    Main Behavee model class providing data from Matomo tracking BBrain and Backend for behavee Partner API."
    """
    __tablename__ = 'partner'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    company_number = db.Column(db.String(255))
    vat_number = db.Column(db.String(255))
    partner_type = db.Column(db.Integer)
    uuid = db.Column(db.String(64))
    deleted = db.Column(db.Boolean, default=False)
    crm = db.relationship('Crm', backref='Partner_Crm')
    market_segment = db.relationship('MarketSegment', backref='Partner_MarketSegment')
    geo_location = db.relationship('GeoLocation', backref='Partner_GeoLocation')
    contact = db.relationship('Contact', backref='Partner_Contact')
    products = db.relationship("ProductPartner", backref='Partner_Product')
    behavee_site = db.relationship('BehaveeSite', backref='Partner_BehaveeSite')
    user_partner = db.relationship('UserPartner', backref='Partner_UserPartner')

    def __repr__(self):
        return '%r' % self.name

    def get_partner_type(self):
        return get_type(PARTNER_TYPE, self.partner_type)

    def post_partner_type(self, enum):
        self.partner_type = post_type(PARTNER_TYPE, enum)
        return True

    def get_country_name(self):
        return get_type(COUNTRY_CODES, self.geo_location[0].country_code)

    def get_geo_location_type(self):
        return get_type(GEO_LOCATION_TYPE, self.geo_location[0].geo_location_type)


class Visitor(db.Model):
    __tablename__ = 'visitor'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    visitor_tracking_id = db.Column(db.String(255), index=True)
    first_visit = db.Column(db.DateTime)
    last_visit = db.Column(db.DateTime)
    partner_id = db.Column(db.String(255))
    has_more_visits = db.Column(db.Integer)
    total_visits = db.Column(db.Integer)
    total_visit_duration = db.Column(db.Integer)
    total_actions = db.Column(db.Integer)
    total_outlinks = db.Column(db.Integer)
    total_downloads = db.Column(db.Integer)
    total_searches = db.Column(db.Integer)
    total_page_views = db.Column(db.Integer)
    total_unique_page_views = db.Column(db.Integer)
    total_revisited_pages = db.Column(db.Integer)
    total_page_views_with_timing = db.Column(db.Integer)
    total_product_purchases = db.Column(db.Integer)
    total_product_refusals = db.Column(db.Integer)
    total_product_views = db.Column(db.Integer)
    total_product_searches = db.Column(db.Integer)
    most_visited_site_name = db.Column(db.String(255))
    most_purchased_product_sku_id = db.Column(db.Integer)
    most_refused_product_sku_id = db.Column(db.Integer)
    most_viewed_product_sku_id = db.Column(db.Integer)
    most_searched_product_sku_id = db.Column(db.Integer)
    last_purchase = db.Column(db.DateTime)
    targeted = db.Column(db.Integer)
    converted = db.Column(db.Integer)
    total_revenue = db.Column(db.Float)
    total_refused_revenue = db.Column(db.Float)
    total_potential_revenue = db.Column(db.Float)
    deleted = db.Column(db.Boolean, default=False)
    visitor_tracking_record = db.relationship('VisitorTrackingRecord', backref='Visitor_Tracking_Record')
    micro_segment = db.relationship('MicroSegment', backref='Visitor_Micro_segment')
    visitor_type = db.Column(db.Integer)
    visitor_product_offer = db.relationship('VisitorProductOffer', backref='Visitor_ProductOffer')
    visitor_product_basket_offer = db.relationship('VisitorProductBasketOffer', backref='Visitor_ProductBasketOffer')
    contact = db.relationship('Contact', backref='Visitor_Contact')

    def __repr__(self):
        return '%r' % self.visitor_tracking_id

    def get_visitor_type(self):
        return get_type(VISITOR_TYPE,self.visitor_type)

    def post_visitor_type(self, enum):
        self.visitor_type = post_type(VISITOR_TYPE, enum)
        return True


class ProductOffer(db.Model):

    __tablename__ = 'product_offer'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime,  default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    visitor_product_offer = db.relationship('VisitorProductOffer', backref="Visitor_VisitorProductOffer")

    def __repr__(self):
        return '%r' % self.id


class ProductBasketOffer(db.Model):
    __tablename__ = 'product_basket_offer'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    visitor_product_basket_offer = db.relationship('VisitorProductBasketOffer', backref="Visitor_VisitorProductBasketOffer")

    def __repr__(self):
        return '%r' % self.id


class VisitorProductOffer(db.Model):
    __tablename__ = 'visitor_product_offer'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id), primary_key=True)
    product_offer_id = db.Column(db.Integer, db.ForeignKey(ProductOffer.id), primary_key=True)
    product_offer = db.relationship('ProductOffer', backref="Visitor_ProductOffer")
    visitor = db.relationship("Visitor", backref="ProductOffer_Visitor")

    def __repr__(self):
        return '%r' % self.id


class VisitorProductBasketOffer(db.Model):
    __tablename__ = 'visitor_product_basket_offer'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id), primary_key=True)
    product_basket_offer_id = db.Column(db.Integer, db.ForeignKey(ProductBasketOffer.id), primary_key=True)
    product_basket_offer = db.relationship('ProductBasketOffer', backref="Visitor_ProductBasketOffer")
    visitor = db.relationship("Visitor", backref="ProductOfferVisitor")

    def __repr__(self):
        return '%r' % self.id


class BehaveeSite(db.Model):
    """
    Main Behavee model class providing data from Matomo tracking BBrain and Backend for site API.
    """
    __tablename__ = 'behavee_site'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tracking_site_id = db.Column(db.Integer, index=True)
    site_name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    first_view = db.Column(db.DateTime,  default=datetime.utcnow)
    last_view = db.Column(db.DateTime,  default=datetime.utcnow)
    no_of_views = db.Column(db.Integer)
    no_of_searches = db.Column(db.Integer)
    average_time_spent = db.Column(db.Integer)
    deleted = db.Column(db.Boolean, default=False)
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id))
    user_site = db.relationship('UserSite', backref='BehaveeSite_UserSite')
    currency =  db.Column(db.Integer)
    site_type = db.Column(db.Integer)
    product_media = db.relationship('ProductMedia', backref='BehaveeSite_ProductMedia')
    content_category = db.relationship('ContentCategory', backref='BehaveeSite_ContentCategory')

    def __repr__(self):
        return '%r' % self.id

    def get_behavee_site_type(self):
        return get_type(SITE_TYPE, self.site_type)

    def post_behavee_site_type(self, enum):
        self.site_type = post_type(SITE_TYPE, enum)
        return True

    def get_behavee_site_currency(self):
        return get_type(CURRENCY, self.currency)

    def post_behavee_site_currency(self, enum):
        self.currency = post_type(CURRENCY, enum)
        return True


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    segment_code = db.Column(db.Integer)
    segment_description = db.Column(db.String(255))
    family_code = db.Column(db.Integer)
    family_description = db.Column(db.String(255))
    class_code = db.Column(db.Integer)
    class_description = db.Column(db.String(255))
    brick_code = db.Column(db.Integer)
    brick_code_description = db.Column(db.String(255))
    product_core_attribute = db.relationship('ProductCoreAttribute', backref='ProductCategory_ProductCoreAttribute')
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))

    def __repr__(self):
        return '%r' % self.id


class ProductCoreAttribute(db.Model):
    __tablename__ = 'product_core_attribute'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.Integer)
    type_description = db.Column(db.String(255))
    product_core_attribute_value = db.relationship('ProductCoreAttributeValue',
                                                   backref='ProductCoreAttribute_ProductCoreAttributeValue')
    product_category_id = db.Column(db.Integer, db.ForeignKey(ProductCategory.id))

    def __repr__(self):
        return '%r' % self.id


class ProductCoreAttributeValue(db.Model):
    __tablename__ = 'product_core_attribute_value'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    value_code = db.Column(db.Integer)
    value_description = db.Column(db.String(255))
    product_core_attribute_id = db.Column(db.Integer, db.ForeignKey(ProductCoreAttribute.id))

    def __repr__(self):
        return '%r' % self.id


class BehaveeUser(db.Model):
    """User is the Actor (Person, System) having the access to Behavee API."""
    __tablename__ = 'behavee_user'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), index=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    token_auth = db.Column(db.String(32), index=True)
    superuser = db.Column(db.Boolean)
    contact = db.relationship('Contact', backref='BehaveeUser_Contact')
    product_history = db.relationship('ProductHistory', backref='BehaveeUser_ProductHistory')
    user_site = db.relationship('UserSite', backref='BehaveeUser_UserSite')
    user_partner = db.relationship('UserPartner', backref='BehaveeUser_UserPartner')
    role = db.Column(db.Integer)

    def __repr__(self):
        return '%r' % self.id

    def get_behavee_user_role(self):
        return get_type(ROLE_TYPE, self.role)

    def post_behavee_user_role(self, enum):
        self.role = post_type(ROLE_TYPE, enum)
        return True


class ProductHistory(db.Model):
    """
    New ProductHistory is created at any change of product metadata.
    ProductHistories are then used for calculation of Product.avaragePrice in chosen time range.
    """
    __tablename__ = 'product_record'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    vat = db.Column(db.Integer)
    currency = db.Column(db.Integer)
    change_time = db.Column(db.DateTime,  default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    behavee_user_id = db.Column(db.Integer, db.ForeignKey(BehaveeUser.id))

    def __repr__(self):
        return '%r' % self.id


class UserSite(db.Model):
    __tablename__ = 'user_site'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey(BehaveeUser.id), primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey(BehaveeSite.id), primary_key=True)
    role = db.Column(db.Integer)
    user = db.relationship('BehaveeUser', backref='UserSite_BehaveeUser')
    site = db.relationship('BehaveeSite', backref='UserSite_BehaveeSite')

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.site_id)

    def get_user_site_role(self):
        return get_type(ROLE_TYPE, self.role)

    def post_user_site_role(self, enum):
        self.role = post_type(ROLE_TYPE, enum)
        return True


class UserPartner(db.Model):
    __tablename__ = 'user_partner'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey(BehaveeUser.id), primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id), primary_key=True)
    role = db.Column(db.Integer)
    user = db.relationship('BehaveeUser', backref='UserPartner_BehaveeUser')
    partner = db.relationship('Partner', backref='UserPartner_Partner')

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.partner_id)

    def get_user_partner_role(self):
        return get_type(ROLE_TYPE, self.role)

    def post_user_partner_role(self, enum):
        self.role = post_type(ROLE_TYPE, enum)
        return True


class ProductMedia(db.Model):
    __tablename__ = 'product_media'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024))
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id))
    behavee_site_id = db.Column(db.Integer, db.ForeignKey(BehaveeSite.id))
    type = db.Column(db.Integer)

    def __repr__(self):
        return '%r' % self.get_product_media_type()

    def get_product_media_type(self):
        return get_type(MEDIA_TYPE, self.type)

    def post_product_meida_type(self, enum):
        self.type = post_type(MEDIA_TYPE, enum)
        return True


class ProductParameter(db.Model):
    """
    Stores information from product bulk upload (post-product.json) such as size, color etc...
    """
    __tablename__ = 'product_parameter'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    value = db.Column(db.String(8096))
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id))

    def __repr__(self):
        return '%r' % self.name


class VisitorTrackingRecord(db.Model):
    __tablename__ = 'visitor_tracking_record'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer)
    from_timestamp = db.Column(db.DateTime, index=True)
    to_timestamp = db.Column(db.DateTime, index=True)
    visit_total_time = db.Column(db.Integer)
    visit_goal_buyer = db.Column(db.Integer)
    visit_goal_converted = db.Column(db.Boolean)
    visit_entry_url = db.Column(db.Text)
    visit_exit_url = db.Column(db.Text)
    visitor_journey_count = db.Column(db.Integer)
    browser_name = db.Column(db.String(255))
    browser_language = db.Column(db.String(255))
    browser_version = db.Column(db.String(255))
    browser_engine = db.Column(db.String(255))
    visitor_tracking_id = db.Column(db.String(64), index=True)
    visit_tracking_id = db.Column(db.Integer, index=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id))
    language = db.Column(db.Integer)

    def __repr__(self):
        return '%r' % self.id

    def get_visitor_tracking_language(self):
        return get_type(LANGUAGES, self.language)

    def post_visior_tracking_language(self, enum):
        self.language = post_type(LANGUAGES, enum)
        return True


class IPAddress(db.Model):
    __tablename__ = 'ip_address'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    visit_tracking_id = db.Column(db.Integer, index=True)
    ip_address = db.Column(db.String(255))

    def __repr__(self):
        return 'id: %r' % self.id


class ProductSales(db.Model):
    __tablename__ = 'product_sales'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.Date, index=True)
    product_sku_id = db.Column(db.Integer)
    product_sku = db.Column(db.String(255))
    product_sku_name = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    value = db.Column(db.Float())
    type = db.Column(db.Integer, index=True)
    position = db.Column(db.Integer)

    def __repr__(self):
        return 'id: %r' % self.id

    def get_sale_type(self):
        return get_type(PRODUCT_TRACKING_TYPE, self.type)

    def post_sale_type(self, enum):
        self.type = post_type(PRODUCT_TRACKING_TYPE, enum)
        return True


class ProductTrackingRecord(db.Model):
    """
    ProductTrackingRecord is created each time of any action (eCommerceOrder, AbandonedCart or Action)
    has been fired on Product.
    """
    __tablename__ = 'product_tracking_record'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id))
    visitor_id = db.Column(db.String(255), index=True)
    visitor_tracking_id = db.Column(db.String(64), index=True)
    visit_tracking_id = db.Column(db.Integer, index=True)
    site_id = db.Column(db.Integer)
    product_sku = db.Column(db.String(255))
    product_sku_name = db.Column(db.String(255))
    price = db.Column(db.Float)
    vat = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    order_id = db.Column(db.String(64))
    time_spent = db.Column(db.Integer)
    search_key = db.Column(db.String(255))
    action_category1 = db.Column(db.String(255))
    action_category2 = db.Column(db.String(255))
    action_category3 = db.Column(db.String(255))
    action_category4 = db.Column(db.String(255))
    action_category5 = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    tracking_action_id = db.Column(db.String(255), index=True)

    def __repr__(self):
        return 'id: %r' % self.id

    def get_product_tracking_type(self):
        return get_type(PRODUCT_TRACKING_TYPE, self.type)

    def post_product_tracking_type(self, enum):
        self.type = post_type(PRODUCT_TRACKING_TYPE, enum)
        return True


class Device(db.Model):
    __tablename__ = 'device'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    operating_system = db.Column(db.String(255))
    browser = db.Column(db.String(255))
    resolution = db.Column(db.String(255))
    visit_tracking_id = db.Column(db.Integer, index=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id))
    device_type = db.Column(db.Integer)

    def __repr__(self):
        return 'id: %r' % self.id

    def get_device_type(self):
        return get_type(DEVICE_TYPE, self.device_type)

    def post_device_type(self, enum):
        self.device_type = post_type(DEVICE_TYPE, enum)
        return True


class Offer(db.Model):
    __tablename__ = 'offer'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)


class MustNotProduct(db.Model):
    __tablename__ = 'must_not_product'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    product = db.relationship('Product', backref="MustNot_Products")
    product_sku = db.relationship('ProductSku', backref="Product_MustNots")

    def __repr__(self):
        return "{} - {}".format(self.product_id, self.product_sku_id)


class MustProduct(db.Model):
    __tablename__ = 'must_product'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    product = db.relationship('Product', backref="Must_Products")
    product_sku = db.relationship('ProductSku', backref="Product_Musts")

    def __repr__(self):
        return "{} - {}".format(self.product_id, self.product_sku_id)


class WishedProduct(db.Model):
    __tablename__ = 'wished_product'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    product = db.relationship('Product', backref="Wished_Products")
    product_sku = db.relationship('ProductSku', backref="Product_Wisheds")


    def __repr__(self):
        return "{} - {}".format(self.product_id, self.product_sku_id)


class SpinOffProduct(db.Model):
    __tablename__ = 'spin_off_product'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    product = db.relationship('Product', backref="SpinOff_Products")
    product_sku = db.relationship('ProductSku', backref="Product_SpinOffs")


    def __repr__(self):
        return "{} - {}".format(self.product_id, self.product_sku_id)


class ProductPartner(db.Model):
    __tablename__ = 'product_partner'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    product_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id), primary_key=True)
    product = db.relationship('Product', backref="Partner_Products")
    partner = db.relationship("Partner", backref="Product_Partners")


class Crm(db.Model):
    __tablename__ = 'crm'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    version = db.Column(db.String(255))
    description = db.Column(db.String(255))
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id))

    def __repr__(self):
        return '%r' % self.name


class MarketSegment(db.Model):
    __tablename__ = 'market_segment'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id))

    def __repr__(self):
        return '%r' % self.name


class Contact(db.Model):
    __tablename__ = 'contact'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    behavee_user_id = db.Column(db.Integer, db.ForeignKey(BehaveeUser.id))
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id))
    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id))
    contact_type = db.Column(db.Integer)

    def __repr__(self):
        return '%r' % self.email

    def get_contact_type(self):
        return get_type(CONTACT_TYPE, self.contact_type)

    def post_contact_type(self, enum):
        self.contact_type = post_type(CONTACT_TYPE, self.contact_type)
        return True


class GeoLocation(db.Model):
    __tablename__ = 'geo_location'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    counts = db.Column(db.Integer)
    continent = db.Column(db.String(255))
    continent_code = db.Column(db.String(255))
    country = db.Column(db.String(255))
    country_code = db.Column(db.String(255))
    city = db.Column(db.String(255))
    street = db.Column(db.String(255))
    street_no = db.Column(db.String(50))
    zip_code = db.Column(db.String(50))
    longitude = db.Column(db.Float(11,8))
    latitude = db.Column(db.Float(10,8))
    visit_tracking_id = db.Column(db.Integer, index=True)
    partner_id = db.Column(db.Integer, db.ForeignKey(Partner.id))
    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id))
    product_sku_id = db.Column(db.Integer, db.ForeignKey(ProductSku.id))
    geo_location_type = db.Column(db.Integer)

    def __repr__(self):
        return 'id: %r' % self.id

    def get_geo_location_type(self):
        return get_type(GEO_LOCATION_TYPE, self.geo_location_type)

    def post_geo_location_type(self, enum):
        self.geo_location_type = post_type(GEO_LOCATION_TYPE, enum)
        return True


class Content(db.Model):
    __tablename__ = 'content'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    url = db.Column(db.String(255))
    content_category = db.relationship('ContentCategory', backref='ContentCategory')
    content_type = db.Column(db.Integer)

    def __repr__(self):
        return 'id: %r' % self.id

    def get_content_type(self):
        return get_type(CONTENT_TYPE, self.content_type)

    def post_contenct_type(self, enum):
        self.content_type = post_type(CONTENT_TYPE, enum)
        return True


class ContentCategory(db.Model):
    """
    Provides the content metadata information - about what is the content
    e.g. Technologies, IoT, Banking, e-commerce, Politics, Fashion...)
    """
    __tablename__ = 'content_category'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    content_id = db.Column(db.Integer, db.ForeignKey(Content.id))
    behavee_site_id = db.Column(db.Integer, db.ForeignKey(BehaveeSite.id))

    def __repr__(self):
        return 'id: %r' % self.id


class MicroSegment(db.Model):
    __tablename__ = 'micro_segment'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    visitor_id = db.Column(db.Integer, db.ForeignKey(Visitor.id))

    def __repr__(self):
        return '%r' % self.name


class VisitorJourney(db.Model):
    __tablename__ = 'visitor_journey'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    visit_tracking_id = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.DateTime,  default=datetime.utcnow)
    visit_entry_url = db.Column(db.String(255))
    visit_exit_url = db.Column(db.String(255))
    interaction_position = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)

    def __repr__(self):
        return 'id: %r' % self.id


# class SiteTrackingRecord(db.Model):
#     __tablename__ = 'site_tracking_record'
#     __bind_key__ = 'portal'
#     __table_args__ = {'extend_existing': True}
#
#     id = db.Column(db.Integer, primary_key=True)
#     tracking_site_id = db.Column(db.Integer, index=True)
#     tracking_visit_id = db.Column(db.Integer, index=True)
#     visitor_id = db.Column(db.String(255))
#     site_search = db.relationship('SiteSearch', backref='SiteSearch')
#     visitor_tracking_record = db.Column(db.Integer, db.ForeignKey(VisitorTrackingRecord.id))
#
#     def __repr__(self):
#         return 'id: %r' % self.id


class SiteSearch(db.Model):
    __tablename__ = 'site_search'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tracking_page_id = db.Column(db.Integer)
    tracking_page_view_id = db.Column(db.String(255))
    search_timestamp = db.Column(db.DateTime,  default=datetime.utcnow)
    #site_tracking_record_id = db.Column(db.Integer, db.ForeignKey(SiteTrackingRecord.id))

    def __repr__(self):
        return 'id: %r' % self.id


class WebSiteView(db.Model):
    __tablename__ = 'website_view'
    __bind_key__ = 'portal'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tracking_page_id = db.Column(db.Integer)
    tracking_page_view_id = db.Column(db.String(255))
    view_timestamp = db.Column(db.DateTime,  default=datetime.utcnow)
    time_spent = db.Column(db.Integer)
    #site_tracking_record_id = db.Column(db.Integer, db.ForeignKey(SiteTrackingRecord.id))

    def __repr__(self):
        return 'id: %r' % self.id


class PartnerUserRel(db.Model):
    __tablename__ = 'partner_user_rel'
    __bind_key__ = 'portal'

    matomo_user_id = db.Column(db.String(255), primary_key=True)
    partner_id = db.Column(db.ForeignKey(Partner.id), nullable=False)


class PartnerUserRelManager:

    @staticmethod
    def get_partner(matomo_user_id) -> Union[Partner,None]:
        try:
            return Partner.query.join(PartnerUserRel).filter(PartnerUserRel.matomo_user_id == matomo_user_id).one()
        except NoResultFound:
            return None
        except:
            # TODO enhance exception handler
            return None

    @staticmethod
    def add(matomo_user_id, *, name, description, company_number, vat_number, partner_type, address_city,
            address_street, address_street_no, address_zip_code, address_latitude, address_longitude,
            address_country_code, address_geo_location_type):
        try:
            partner = Partner(
                name=name,
                description=description,
                company_number=company_number,
                vat_number=vat_number,
                partner_type=partner_type,
                uuid=str(uuid4())
            )
            db.session.add(partner)
            db.session.flush()

            rel = PartnerUserRel(matomo_user_id=matomo_user_id, partner_id=partner.id)
            db.session.add(rel)

            address = GeoLocation(
                city=address_city,
                street=address_street,
                street_no=address_street_no,
                zip_code=address_zip_code,
                country_code=address_country_code,
                geo_location_type=address_geo_location_type,
                partner_id=partner.id,
            )
            db.session.add(address)

            db.session.commit()

        except Exception as e:
            # TODO log exception
            db.session.rollback()

    @staticmethod
    def update(matomo_user_id, *, name, description, company_number, vat_number, partner_type, address_city,
               address_street, address_street_no, address_zip_code, address_latitude, address_longitude,
               address_country_code, address_geo_location_type):

        partner = Partner.query.join(PartnerUserRel).filter(PartnerUserRel.matomo_user_id == matomo_user_id).one()

        partner.name = name
        partner.description = description
        partner.company_number = company_number
        partner.vat_number = vat_number
        partner.partner_type = partner_type

        if partner.geo_location:
            partner.geo_location[0].city = address_city
            partner.geo_location[0].street = address_street
            partner.geo_location[0].street_no = address_street_no
            partner.geo_location[0].zip_code = address_zip_code
            partner.geo_location[0].country_code = address_country_code
            partner.geo_location[0].geo_location_type = address_geo_location_type

        else:
            geolocation = GeoLocation(
                city=address_city,
                street=address_street,
                street_no=address_street_no,
                zip_code=address_zip_code,
                country_code=address_country_code,
                geo_location_type=address_geo_location_type,
            )
            partner.geo_location.append(geolocation)

        try:
            db.session.commit()
        except Exception as e:
            # TODO log exception
            db.session.rollback()
