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

#####################
# Auth toggle
#
# IF NO - the app is completely insecure.  It will allow you to sign in an any 'user'
# and gain access to all their projects simply by entering their usernam on the logon
# screen.

# IF YES - then the app assumes it is running behind an auth'd proxy and will expect
# {REMOTE_USER_HEADER_KEY} to be in the request headers.  If the value of
# {REMOTE_USER_HEADER_KEY} matches entries in user_list associated with each project
# then that user will be granted access to that project
#####################
AUTH_ENABLED='no'

####################
# logging config
####################
# Can be any valid filesystem path
LOGFILE_LOCATION = 'log/flask_server.log'
LOGGER_NAME = 'pv_logger'

###################
# Image directory
# defaulted to work with example data
# Needs updated for your projects
###################
IMAGE_DIR = 'example_database/img'

##################
# Configure the key your proxy uses
# to send current auth'd user in REMOTE USER variable
# a few common iterations below
##################
REMOTE_USER_HEADER_KEY = 'REMOTE_USER'
# REMOTE_USER_HEADER_KEY = 'Remote_User'
# REMOTE_USER_HEADER_KEY = 'X-REMOTE_USER'

#################
# Data source config
# mongo connect dict is for the app
# create proj mongo connect dict is for the create project script
# depending on how you are running the create project script, it may require slightly different
# connection paramaters, notably 'host' since the app will be connecting accross a 
# docker network, net_pv, and the create project script could be run from anywhere
#################
MONGO_CONNECT_DICT={"host":"mongo",
    "port":27017,
    "user":'',
    "pass":'',
    "auth_source":''}

CREAT_PROJ_MONGO_CONNECT_DICT={"host":"localhost",
    "port":27017,
    "user":'',
    "pass":'',
    "auth_source":''}

DB_NAME='pv_db'
USER_COLLECTION_NAME='users'
PROJECT_COLLECTION_NAME='projects'
PROJECT_DATA_COLLECTION_NAME='project_data'
