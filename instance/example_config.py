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

#################
# Data source config
#################
MONGO_CONNECT_DICT={"host":"mongo",
    "port":27017,
    "user":'',
    "pass":'',
    "auth_source":''}
DB_NAME='pv_db'
USER_COLLECTION_NAME='users'
PROJECT_COLLECTION_NAME='projects'
PROJECT_DATA_COLLECTION_NAME='project_data'
