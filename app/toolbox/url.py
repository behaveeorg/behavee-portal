from flask import url_for, request

from app import app
from app.constants import URL_FOR_ARGS


def behavee_url_for(endpoint, **values):
    """
    An `flask.url_for` wrapper that automatically adds the required params
    defined in `app.constants.URL_FOR_ARGS`
    """
    args = request.args.to_dict()

    for item in URL_FOR_ARGS:
        if item in args and item not in values:
            values[item] = args[item]

    return url_for(endpoint, **values)


@app.context_processor
def behavee_url_for_processor():
    return {
        'behavee_url_for': behavee_url_for
    }
