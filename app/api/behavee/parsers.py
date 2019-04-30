import werkzeug
from app.api.restplus import api
from werkzeug.exceptions import BadRequest

pagination_arguments = api.parser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('bool', type=bool, required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, choices=[2, 10, 20, 30, 40, 50],
                                  default=10, help='Results per page {error_msg}')

auth_token_help = 'API Authentication token [token_auth]'
upload_file_help = 'XML file'
limit_help = 'limit of products returned in one request'
offset_help = 'offset (first 100 products, second 100 products etc)'
date_help = 'YYYY-MM-DD'

empty_parser = api.parser()

token_parser = empty_parser.copy()
token_parser.add_argument('token_auth', required=True, help=auth_token_help, type=str, location='headers')

file_parser = token_parser.copy()
file_parser.add_argument('xml_file', required=True, help=upload_file_help, type=werkzeug.datastructures.FileStorage, location='files')

page_parser = token_parser.copy()
page_parser.add_argument('limit', help=limit_help, type=int, location='args')
page_parser.add_argument('offset', help=offset_help, type=int, location='args')

date_parser = token_parser.copy()
date_parser.add_argument('from_date', type=str, help=date_help, location='args')
date_parser.add_argument('to_date', type=str, help=date_help, location='args')

e401 = BadRequest('Unauthorized')
e401.code = 401
e401.data = {'message': 'Autentication token is not authorized to do this action'}

e404 = BadRequest('Not Found')
e404.code = 404

e500 = BadRequest('Internal Server Error')
e500.code = 500
