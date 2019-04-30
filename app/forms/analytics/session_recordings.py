from wtforms import fields, validators

from app import constants
from app.toolbox.forms import Form


class SessionRecordingForm(Form):
    name = fields.StringField('Name', [validators.required(), validators.length(max=50)])
    sample_limit = fields.SelectField(
        'Number of sessions', choices=constants.SESSION_RECORDING_SAMPLE_LIMIT, coerce=int, default=1000)
    sample_rate = fields.SelectField(
        'Sample Rate', choices=constants.SESSION_RECORDING_SAMPLE_LIMIT, default=10.0, coerce=float
    )
    min_session_time = fields.SelectField(
        'Min Session Time', choices=constants.SESSION_RECORDING_MIN_SESSION_TIME, default=0, coerce=int,
    )
    requires_activity = fields.SelectField(choices=(('0', 'No'), ('1', 'Yes'),), default='1')
    capture_keystrokes = fields.SelectField(choices=(('0', 'No'), ('1', 'Yes'),), default='1')

    @classmethod
    def with_rules(cls, number_of_rules, **kwargs):
        """
        Creates a new form class with the rules fields and returns an instance of that class.
        **kwargs are passed to the __init__ of the new class.
        """

        class SessionRecordingWithRulesForm(cls):
            pass

        for i in range(number_of_rules):
            setattr(SessionRecordingWithRulesForm, f'rules_attribute_{i}',
                    fields.SelectField(choices=constants.RULES))
            setattr(SessionRecordingWithRulesForm, f'rules_type_{i}',
                    fields.SelectField(choices=constants.RULES_TYPE))
            setattr(SessionRecordingWithRulesForm, f'rules_value_{i}',
                    fields.StringField())
            setattr(SessionRecordingWithRulesForm, f'rules_value2_{i}',
                    fields.StringField())

        return SessionRecordingWithRulesForm(**kwargs)


class SessionRecordingDeleteForm(Form):
    name = fields.StringField('Session Recording Name')