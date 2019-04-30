from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, fields
from wtforms.validators import DataRequired

from app import constants
from app.toolbox.forms import MultiValueTextField, Form


class WebsiteForm(Form):
    name = StringField('Site name', validators=[DataRequired()], render_kw={"placeholder": "MySite"})
    main_url = StringField('Tracked URL', validators=[DataRequired()], default='', render_kw={"placeholder": "https://www.example.com"})

    exclude_unknown_urls = SelectField(
        "Exclude unknown URLS: ",
        choices=[("0", "No"), ("1", "Yes")],
        default=1,
        render_kw = {"title": "When enabled, Behavee will only track internal actions when the Page URL is one of the known URLs for your website. "
                              "\n\nThis prevents people from spamming your analytics with URLs for other websites. "
                              "\nThe domain and the path has to be an exact match and each valid subdomain has to be specified separately. "
                              "\nFor example when the known URLs are 'http://example.com/path' and 'http://good.example.com', "
                              "tracking requests for 'http://example.com/otherpath' or 'http://bad.example.com' are ignored."}
    )

    excluded_ips = MultiValueTextField(
        'Excluded IPs - list of IP address, you don\'t want to track',
        description='Please provide the parameters as a comma separated list of IP\'s',
        render_kw = {"placeholder": "Enter the list of IPs, one per line, that you wish to exclude from being tracked by Behavee."
                                    "\n\nYou can use CIDR notation eg. 1.2.3.4/24 or you can use wildcards, eg. 1.2.3.* or 1.2.*.*"}
    )
    excluded_parameters = MultiValueTextField(
        'Excluded parameters',
        description='Please provide the parameters as a comma separated list of values',
        render_kw={"placeholder": "Enter the list of URL Query Parameters, one per line, to exclude from the Page URLs reports."
                                  "\n\nRegular expressions such as  /^sess.*|.*[dD]ate$/ are supported. "
                                  "\nBehavee will automatically exclude the common session parameters (phpsessid, sessionid, ...)."}
    )
    excluded_user_agents = MultiValueTextField(
        'Excluded user agents',
        description='Please provide the user agents as a comma separated list of values',
        render_kw={"placeholder": "Enter the list of user agents to exclude from being tracked by Behavee"
                                  "\n\nIf the visitor's user agent string contains any of the strings you specify, the visitor will be excluded from Behavee."
                                  "\nYou can use this to exclude some bots from being tracked."}
    )
    sitesearch_keyword_parameters = MultiValueTextField(
        'Search keyword parameters',
        description='Please provide the search keyword parameters as a comma separated list of values',
        default='q,query,s,search,searchword,k,keyword,hledat',
        render_kw={"placeholder": "Enter a comma separated list of all query parameter names containing the site search keyword."
                                  "\n\neg: q,query,s,search,searchword,k,keyword,hledat"}
    )
    sitesearch_category_parameters = MultiValueTextField(
        'Search category parameters',
        description='Please provide the search category parameters as a comma separated list of values',
        render_kw={"placeholder": "(optional)"
                                  "\n\nYou may enter a comma-separated list of query parameters specifying the search category."}
    )
    sitesearch = SelectField(
        "Site search: ",
        choices=[('0', "Do not track Site Search"), ('1', "Site Search tracking enabled")],
        default=1,
        render_kw = {"title": "You can use Behavee to track and report what visitors are searching in your website's internal search engine. "}
    )

    ecommerce = SelectField(
        "Ecommerce site: ",
        choices=[('0', "Not an ecommerce site"), ('1', "Ecommerce enabled")],
        default=0,
        render_kw = {"title": "When enabled, you will have Ecommerce, Products, Sales and Goals sections enabled."
                              "\nBehavee allows for advanced Ecommerce Analytics tracking & reporting."}
    )
    keep_url_fragments = SelectField(
        "Keep Page URL fragments when tracking Page URLs: ",
        choices=[('0', "Do not keep fragments"), ('1', "Keep URL fragments")],
        render_kw={"title": "Keep Page URL fragments when tracking Page URLs"}
    )
    currency = SelectField("Currency: ", choices=constants.WEBSITE_CURRENCY)
    timezone = SelectField("Timezone: ", choices=constants.WEBSITE_TIMEZONE)

    package = SelectField("Package", coerce=int, validators=[DataRequired()])

    @classmethod
    def with_packages(cls, package_choices, **kwargs):
        form = cls(**kwargs)
        form.package.choices = package_choices
        return form


class SiteDeleteForm(FlaskForm):
    name = fields.StringField('Site Name')
