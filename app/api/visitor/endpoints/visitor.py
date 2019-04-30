import logging

from flask import request, abort
from flask_restplus import Resource
from app.api.visitor.serializers import logvisit_location
from app.api.restplus import api
from app import User
from app.api.visitor.business import getLastLocation

log = logging.getLogger(__name__)
ns = api.namespace('tracking', path='/visitor', description='Operations related to visits')

parser = api.parser()
auth_token_help = 'API Authentication token <token_auth>'
parser.add_argument('token_auth', required=True, help=auth_token_help, type=str, location='headers')

# create copy of parser and add payload, for POST and PUT methods
parser_payload = parser.copy()
parser_payload.add_argument('Payload', required=True, help='JSON Payload', type='list', location='json')


@ns.route('/<string:visitor_id>/location')
@api.response(200, 'OK')
@api.response(404, 'Not Found')
@api.response(503, 'Service Unavailable')
class VisitorLastLocation(Resource):

    @api.doc(parser=parser)
    @api.marshal_with(logvisit_location)
    def get(self, visitor_id):
        """
        Returns last location of visitor.
        """

        # only for validated users with Authorization request header
        token_auth = request.headers['token_auth']
        r = getLastLocation(token_auth, visitor_id)

        return r, 200