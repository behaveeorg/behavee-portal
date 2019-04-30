from wtforms import fields, validators

from app.constants import PARTNER_TYPE, GEO_LOCATION_TYPE, COUNTRY_CODES
from app.toolbox.forms import Form, choices_from_enum


class PartnerForm(Form):
    name = fields.StringField('Company Name', validators=[validators.required(), validators.length(max=255)], render_kw={"placeholder": "Insert your company or personal name"})
    description = fields.StringField('Description', render_kw={"placeholder": "Company description"})
    company_number = fields.StringField('Company registration', render_kw={"placeholder": "Company registration ID"})
    vat_number = fields.StringField('VAT number', render_kw={"placeholder": "VAT registration ID"})
    partner_type =  fields.SelectField('Partner Type', validators=[validators.required()], choices=PARTNER_TYPE, default=2)
    address_city = fields.StringField('City', validators=[validators.required(), validators.length(max=255)])
    address_street = fields.StringField('Street', validators=[validators.required(), validators.length(max=255)])
    address_street_no = fields.StringField(
        'Street Number', validators=[validators.required(), validators.length(max=50)])
    address_zip_code = fields.StringField('ZIP Code', validators=[validators.required(), validators.length(max=50)])
    address_longitude = fields.FloatField('Longitude')
    address_latitude = fields.FloatField('Latitude')
    address_country_code = fields.SelectField(
        'Country', validators=[validators.required(), validators.length(max=255)], choices=COUNTRY_CODES, default='CZ')
    address_geo_location_type = fields.SelectField(
        'Type', validators=[validators.required()], choices=GEO_LOCATION_TYPE,  default=2)
