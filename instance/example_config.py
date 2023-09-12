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
RUN_MODE='dev'
# RUN_MODE='dev'

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
