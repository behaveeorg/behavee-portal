from wtforms import fields, validators

from app import constants
from app.toolbox.forms import MultiValueTextField, Form


class HeatmapForm(Form):
    name = fields.StringField('Name', [validators.required(), validators.length(max=50)])
    sample_limit = fields.SelectField('Number of page views', choices=constants.HEATMAP_SAMPLE_LIMIT, coerce=int)
    sample_rate = fields.SelectField('Sample Rate', choices=constants.HEATMAP_SAMPLE_RATES, default=15.0, coerce=float)
    excluded_elements = MultiValueTextField('Excluded Elements')
    screenshot_url = fields.StringField('Screenshot URL', [validators.length(max=300)])
    breakpoint_mobile = fields.StringField('Breakpoint Mobile', default='600')
    breakpoint_tablet = fields.StringField('Breakpoint Tablet', default='960')

    @classmethod
    def with_rules(cls, number_of_rules, **kwargs):
        """
        Creates a new form class with the rules fields and returns an instance of that class.
        **kwargs are passed to the __init__ of the new class.
        """

        class HeatmapWithRulesForm(cls):
            pass

        for i in range(number_of_rules):
            setattr(HeatmapWithRulesForm, f'rules_attribute_{i}', fields.SelectField(choices=constants.RULES))
            setattr(HeatmapWithRulesForm, f'rules_type_{i}', fields.SelectField(choices=constants.RULES_TYPE))
            setattr(HeatmapWithRulesForm, f'rules_value_{i}', fields.StringField())
            setattr(HeatmapWithRulesForm, f'rules_value2_{i}', fields.StringField())

        return HeatmapWithRulesForm(**kwargs)

    # breakpoint_mobile = fields.StringField()


class HeatmapsDeleteForm(Form):
    name = fields.StringField('Heatmap Name')
