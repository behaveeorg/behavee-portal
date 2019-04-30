import sys, os, logging
from pathlib import Path


def _load_this_env():
    try:
        if sys.argv[0] == 'run':
            return str(sys.argv[1])
    except IndexError:
        pass

    try:
        return os.environ['BEHAVEE_ENV']
    except KeyError:
        pass

    return 'local'

this_env = _load_this_env()

if this_env == 'prod':
    from app.config_prod import *
elif this_env == 'test':
    from app.config_test import *
else:
    raise RuntimeError('Invalid environment {}'.format(this_env))

BASE_DIR = Path(__file__).parent

# Common settings
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Flask-Session
SESSION_COOKIE_NAME = '$SESSION_COOKINE_NAME'
SESSION_TYPE = 'sqlalchemy'
SESSION_SQLALCHEMY_TABLE = 'sessions'
PERMANENT_SESSION_LIFETIME = 3600

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list' # none|list|full
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Set flask admin swatch, themes from https://bootswatch.com/
FLASK_ADMIN_SWATCH = 'cerulean'

# Number of times a password is hashed
BCRYPT_LOG_ROUNDS = 7

# server timezone
LC_TIME="en_US.UTF-8"

# Salts for email tokens
EMAIL_CONFIRM_SALT  = '$EMAIL_CONFIRM_SALT'
EMAIL_RESET_SALT    = '$EMAIL_RESET_SALT'
EMAIL_FORGOT_SALT   = '$EMAIL_FORGOT_SALT'

# Flask-Security Core
SECURITY_BLUEPRINT_NAME	= 'security' # Specifies the name for the Flask-Security blueprint. Defaults to security.
SECURITY_CLI_USERS_NAME	= False      # Specifies the name for the command managing users. Disable by setting False. Defaults to users.
SECURITY_CLI_ROLES_NAME	= False      # Specifies the name for the command managing roles. Disable by setting False. Defaults to roles.
SECURITY_URL_PREFIX     = None       # Specifies the URL prefix for the Flask-Security blueprint. Defaults to None.
SECURITY_SUBDOMAIN      = None       # Specifies the subdomain for the Flask-Security blueprint. Defaults to None.
SECURITY_FLASH_MESSAGES	= True       # Specifies whether or not to flash messages during security procedures. Defaults to True.
SECURITY_I18N_DOMAIN	= 'flask_security'    # Specifies the name for domain used for translations. Defaults to flask_security.
SECURITY_PASSWORD_HASH	= 'bcrypt'   # Specifies the password hash algorithm to use when hashing passwords. Recommended values for production systems are bcrypt,
                                     # sha512_crypt, or pbkdf2_sha512. Defaults to bcrypt.
SECURITY_PASSWORD_SALT	= '$SECURITY_PASSWORD_SALT'       # Specifies the HMAC salt. This is only used if the password hash type is set to something other than plain text. Defaults to None.
SECURITY_PASSWORD_SINGLE_HASH = False   # Specifies that passwords should only be hashed once. By default, passwords are hashed twice,
                                        # first with SECURITY_PASSWORD_SALT, and then with a random salt. May be useful for integrating with other applications. Defaults to False.
SECURITY_EMAIL_SENDER	            = '$SECURITY_EMAIL_SENDER'    # Specifies the email address to send emails as. Defaults to value set to MAIL_DEFAULT_SENDER if Flask-Mail is used otherwise no-reply@localhost.
SECURITY_TOKEN_AUTHENTICATION_KEY	= 'token_auth'    # Specifies the query string parameter to read when using token authentication. Defaults to token_auth.
SECURITY_TOKEN_AUTHENTICATION_HEADER= 'Authentication-Token'    # Specifies the HTTP header to read when using token authentication. Defaults to Authentication-Token.
SECURITY_TOKEN_MAX_AGE	            = None    # Specifies the number of seconds before an authentication token expires. Defaults to None, meaning the token never expires.
SECURITY_DEFAULT_HTTP_AUTH_REALM	= 'Login Required'    # Specifies the default authentication realm when using basic HTTP auth. Defaults to Login Required

# Flask-Security URLs and Views
SECURITY_LOGIN_URL          = '/login/'    # Specifies the login URL. Defaults to /login.
SECURITY_LOGOUT_URL         = '/logout/'   # Specifies the logout URL. Defaults to /logout.
SECURITY_REGISTER_URL	    = '/register/' # Specifies the register URL. Defaults to /register.
SECURITY_RESET_URL          = '/reset/'    # Specifies the password reset URL. Defaults to /reset.
SECURITY_CHANGE_URL         = '/change/'   # Specifies the password change URL. Defaults to /change.
SECURITY_CONFIRM_URL	    = '/confirm/'  # Specifies the email confirmation URL. Defaults to /confirm.
SECURITY_POST_LOGIN_VIEW	= '/'   # Specifies the default view to redirect to after a user logs in. This value can be set to a URL or an endpoint name. Defaults to /.
SECURITY_POST_LOGOUT_VIEW	= '/'   # Specifies the default view to redirect to after a user logs out. This value can be set to a URL or an endpoint name. Defaults to /.
SECURITY_CONFIRM_ERROR_VIEW	= None  # Specifies the view to redirect to if a confirmation error occurs. This value can be set to a URL or an endpoint name.
SECURITY_POST_REGISTER_VIEW	= None  # Specifies the view to redirect to after a user successfully registers. This value can be set to a URL or an endpoint name.
SECURITY_POST_CONFIRM_VIEW	= None  # Specifies the view to redirect to after a user successfully confirms their email. This value can be set to a URL or an endpoint name.
SECURITY_POST_RESET_VIEW	= None  # Specifies the view to redirect to after a user successfully resets their password. This value can be set to a URL or an endpoint name.
SECURITY_POST_CHANGE_VIEW	= None  # Specifies the view to redirect to after a user successfully changes their password. This value can be set to a URL or an endpoint name.
SECURITY_UNAUTHORIZED_VIEW	= None  # Specifies the view to redirect to if a user attempts to access a URL/endpoint that they do not have permission to access.

# Flask-Security Template Paths
SECURITY_FORGOT_PASSWORD_TEMPLATE	= 'security/forgot_password.html'    # Specifies the path to the template for the forgot password page. Defaults to security/forgot_password.html.
SECURITY_LOGIN_USER_TEMPLATE	    = 'security/login_user.html'    # Specifies the path to the template for the user login page. Defaults to security/login_user.html.
SECURITY_REGISTER_USER_TEMPLATE	    = 'security/register_user.html'    # Specifies the path to the template for the user registration page. Defaults to security/register_user.html.
SECURITY_RESET_PASSWORD_TEMPLATE	= 'security/reset_password.html'    # Specifies the path to the template for the reset password page. Defaults to security/reset_password.html.
SECURITY_CHANGE_PASSWORD_TEMPLATE	= 'security/change_password.html'    # Specifies the path to the template for the change password page. Defaults to security/change_password.html.
SECURITY_SEND_CONFIRMATION_TEMPLATE	= 'security/send_confirmation.html'    # Specifies the path to the template for the resend confirmation instructions page. Defaults to security/send_confirmation.html.
SECURITY_SEND_LOGIN_TEMPLATE	    = 'security/send_login.html'    # Specifies the path to the template for the send login instructions page for passwordless logins. Defaults to security/send_login.html.

# Flask-Security Feature Flags
SECURITY_CONFIRMABLE	= True  # Specifies if users are required to confirm their email address when registering a new account.
SECURITY_REGISTERABLE	= True  # Specifies if Flask-Security should create a user registration endpoint.
SECURITY_RECOVERABLE	= True  # Specifies if Flask-Security should create a password reset/recover endpoint.
SECURITY_TRACKABLE	    = True  # Specifies if Flask-Security should track basic user login statistics.
SECURITY_PASSWORDLESS	= True # Specifies if Flask-Security should enable the passwordless login feature.
SECURITY_CHANGEABLE	    = True # Specifies if Flask-Security should enable the change password endpoint.

# Flask-Security Email
SECURITY_EMAIL_SUBJECT_REGISTER	= 'Welcome to behavee.com'    # Sets the subject for the confirmation email. Defaults to Welcome
SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE	= 'Your password has been reset'    # Sets subject for the password notice. Defaults to Your password has been reset
SECURITY_EMAIL_SUBJECT_PASSWORD_RESET	= 'Password reset instructions'    # Sets the subject for the password reset email. Defaults to Password reset instructions
SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE	= 'Your password has been changed'    # Sets the subject for the password change notice. Defaults to Your password has been changed
SECURITY_EMAIL_SUBJECT_CONFIRM	= 'Please confirm your email'    # Sets the subject for the email confirmation message. Defaults to Please confirm your email
SECURITY_EMAIL_PLAINTEXT = False    # Sends email as plaintext using *.txt template. Defaults to True.
SECURITY_EMAIL_HTML = True          # Sends email as HTML using *.html template. Defaults to True.

# Flask-Security Miscellaneous
SECURITY_USER_IDENTITY_ATTRIBUTES	= ['email']    # Specifies which attributes of the user object can be used for login. Defaults to ['email'].
SECURITY_SEND_REGISTER_EMAIL	    = True    # Specifies whether registration email is sent. Defaults to True.
SECURITY_SEND_PASSWORD_CHANGE_EMAIL	= True    # Specifies whether password change email is sent. Defaults to True.
SECURITY_SEND_PASSWORD_RESET_EMAIL	= True    # Specifies whether password reset email is sent. Defaults to True.
SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL	= True    # Specifies whether password reset notice email is sent. Defaults to True.
SECURITY_CONFIRM_EMAIL_WITHIN	= '1 days'    # Specifies the amount of time a user has before their confirmation link expires. Always pluralized the time unit for this value. Defaults to 5 days.
SECURITY_RESET_PASSWORD_WITHIN	= '1 days'    # Specifies the amount of time a user has before their password reset link expires. Always pluralized the time unit for this value. Defaults to 5 days.
SECURITY_LOGIN_WITHIN	= '1 days'            # Specifies the amount of time a user has before a login link expires. This is only used when the passwordless login feature is enabled.
                                              # Always pluralized the time unit for this value. Defaults to 1 days.
SECURITY_LOGIN_WITHOUT_CONFIRMATION	= False   # Specifies if a user may login before confirming their email when the value of SECURITY_CONFIRMABLE is set to True. Defaults to False.
SECURITY_CONFIRM_SALT	    = '$SECURITY_CONFIRM_SALT'                  # Specifies the salt value when generating confirmation links/tokens. Defaults to confirm-salt.
SECURITY_RESET_SALT	        = '$SECURITY_RESET_SALT'    # Specifies the salt value when generating password reset links/tokens. Defaults to reset-salt.
SECURITY_LOGIN_SALT	        = '$SECURITY_LOGIN_SALT'    # Specifies the salt value when generating login links/tokens. Defaults to login-salt.
SECURITY_REMEMBER_SALT	    = '$SECURITY_REMEMMBER_SALT'# Specifies the salt value when generating remember tokens. Remember tokens are used instead of user ID’s as it is more secure. Defaults to remember-salt.
SECURITY_DEFAULT_REMEMBER_ME= False    # Specifies the default “remember me” value used when logging in a user. Defaults to False.
