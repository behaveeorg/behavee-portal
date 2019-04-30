from enum import Enum

from flask_wtf import FlaskForm
from wtforms import Field, widgets


class Form(FlaskForm):
    @property
    def data(self):
        data = super().data

        try:
            data.pop('csrf_token')  # Remove CSRF token from form data
        except KeyError:
            pass

        return data


class MultiValueTextField(Field):
    widget = widgets.TextArea()

    def _value(self):
        if isinstance(self.data, str):
            self.data = self.data.split(',')

        if self.data:
            return '\n'.join(self.data)

        return ''

    def process_formdata(self, valuelist):
        data = set()
        if valuelist:
            for item in valuelist[0].splitlines():
                item = item.strip()
                if item:
                    data.add(item)

        self.data = list(data)


def choices_from_enum(item: Enum):
    return [(i.value, i.name) for i in item]