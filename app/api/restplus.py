import traceback
from flask import url_for
from flask_restplus import Api
from sqlalchemy.orm.exc import NoResultFound
from app import app
import logging.config

log = logging.getLogger(__name__)

class Custom_Api(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

api = Custom_Api(version='v1', title='Behavee API', description='An API interface to Behavee products')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not app.config['FLASK_DEBUG']:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'Not Found'}, 404
