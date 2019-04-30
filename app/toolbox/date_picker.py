import json
from datetime import datetime

from flask import request

from app import app


def _parse_args():
    """ Private function used to parse the value. We use this logic to simplify reading """
    period = request.args.get('period')
    date = label = request.args.get('date')

    if date is None:
        date = label = datetime.now().date().isoformat()

    if period in ['range', 'week']:
        label = date.split(',')
        return ' &mdash; '.join(label), label

    label = label.split('-')

    if period == 'year':
        return label[0], [date]
    if period == 'month':
        return '-'.join(label[:2]), [date]
    elif period == 'day':
        pass

    return '-'.join(label), [date]


@app.context_processor
def date_picker_value():
    label, value = _parse_args()
    return {
        'date_picker_label': label,
        'date_picker_value': value,
        'date_picker_period': request.args.get('period', ''),
    }
