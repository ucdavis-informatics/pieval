########################################################
# config file
########################################################
##################
# Flask app config
##################
BLUEPRINT_URL_PREFIX = '/pieval'
# This key is used to sign the session object passed between client and server
# Make this sufficiently long and random
SECRET_KEY = 'super_secret_key'

####################
# logging config
####################
# Can be any valid filesystem path
LOGFILE_LOCATION = 'example_log/flask_server.log'
LOGGER_NAME = 'pv_logger'

##################
# Run Mode config
"""
Run Mode : toggle between Dev/Demo and Production modes
Run Mode primarily impacts how Auth is wired up
- When run in prod mode, wire into a secure instance of keycloak that may or may not be running in a container depending on your deployment
- When run in dev mode, wire into a non-secure instance of keycloak that runs in a sibling docker container to the pieval app
  and is auto-configured with default settings and credentials on startup

To alter which instance we are wired into we need only to change the point to the 'client secrets' file.
The contents of this file contains pointers to the correct instance
"""
##################
RUN_MODE='dev' # 'prod'
OIDC_CLIENT_SECRETS = None
if RUN_MODE == 'dev':
    OIDC_CLIENT_SECRETS = 'instance/client_secrets_dev.json'
    KC_USER='admin'
    KC_PASS='admin'
    KC_REALM_URL="http://pv_kc:8443/auth/admin/realms"
    KC_TOK_URL="http://pv_kc:8443/auth/realms/master/protocol/openid-connect/token"
    KC_REALM_JSON="docker_kc/resources/pieval_realm.json"
    KC_CLIENT_JSON="docker_kc/resources/pieval_client.json"
    KC_USER_JSON="docker_kc/resources/pieval_user.json"
    OIDC_OPENID_REALM = 'pieval_realm'
elif RUN_MODE == 'prod':
    OIDC_CLIENT_SECRETS = 'instance/client_secrets.json'
    OIDC_OPENID_REALM = 'cdi3'
else:
    OIDC_CLIENT_SECRETS = None


# KeyCloak config that is the same no matter what
OIDC_ID_TOKEN_COOKIE_SECURE = False
OIDC_REQUIRE_VERIFIED_EMAIL = False
OIDC_USER_INFO_ENABLED = True
OIDC_SCOPES = ['openid', 'email', 'profile']
OIDC_INTROSPECTION_AUTH_METHOD = 'client_secret_post'
OIDC_CALLBACK_ROUTE = '/pieval/oidc_callback'


#################
# Data source config
#################
'''
The persistence layer can be either filesystem (csv files) or and RDMBS database
The file system approach is good for feature development but not appropriate for
production deployments

For prod deployments:
- change DATASOURCE_TYPE = 'db'
- change DATASOURCE_LOCATION to the vault path of the secrets for your desired database

UCD runs Vault (https://www.vaultproject.io) that provides secrets as a service rather than
storing secrets with the applicaion in a file such as this one.  we understand the choice to 
bind this to vault may be an impediment to usage.  Please keep in mind a few alternatives:
1. You can store your secrets in this file rather than using vault.  to do this you will need to:
    - modify data_loader.py (init_pv_dl) and the call to it in wsgi.py to slurp up secrets directly from this file
2. Use the csv file based backend accepting the limitation that you can only allow one user at a time to
annotate when running the app in this way.
'''
# options ['db','file']
DATASOURCE_TYPE = 'file'

# value is either filesystem if DATASOURCE_TYPE == 'file' path or vault path if DATASOURCE_TYPE == 'db'
DATASOURCE_LOCATION = 'example_database/'

IMAGE_DIRECTORY='/pieval/example_database/example_annot_images/'
# defaulted to pieval.
# Change this is you want to place tables in a different schema
# only relevant if DATASOURCE_TYPE == 'db'
DB_SCHEMA = 'pieval'

# Vault - when prod wire up to a Persistent instance
# only relevant if DATASOURCE_TYPE == 'db'
VAULT_SERVER = '<vault host url>'
VAULT_ROLE_ID = '<vault role id>'
VAULT_SECRET_ID = '<vault secret id>'
VAULT_SECRET_ID_ACCESSOR = '<vault secret id accessor>'

#####################
# Background task config
"""
Think of these as events that take place at routine intervals.  In Pieval
we use background tasks to do 2 things:
1. Remind annotators that they have work to do, after a period of inactivity
2. Keep the auth token active to retain access to the database secrets
"""
######################
TOKEN_REFRESH = 13  # units match what's declared below for the job interval - Hours
# Host FQDN is used to provide a link in reminder emails.  The app does not use is
HOST_FQDN='https://yourhost.something.biz'
FROM_EMAIL = 'email@email.com'
IGNORE_SEND = False
DAYS_TILL_PROMPT = 2
JOBS = [
        {
            'id': 'annotation_reminder',
            'func': 'send_reminders:send_reminders',
            'trigger': 'cron',
            'day_of_week': 'mon-fri',
            'hour': '09'
        },
        {
            'id': 'token_renew',
            'func': 'renew_token:renew_token',
            'trigger': 'interval',
            'hours': TOKEN_REFRESH
        }
    ]

