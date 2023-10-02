"""
Author: Bill Riedl
Purpose: Entrypoint for DEV mode app launch
"""
#!flask/bin/python
# Import app variable from our app package
import time
import random
import logging
import os
from pathlib import Path
from itertools import chain
from pymongo import MongoClient

# 'sibling' files
# app module
import app.wsgi as wsgi
from app.data_loader import get_mongo_client
import create_project


def create_app():
    time.sleep(random.uniform(0.2,1.5))
    app = wsgi.create_app()
    logger = logging.getLogger(app.config['LOGGER_NAME'])
    logger.info("Logger Configured")
    return app

if __name__ == '__main__':
    # DEVELOPMENT (Internal-facing, Debug on)
    os.environ['FLASK_ENV']='development'

    app = create_app()
    logger = logging.getLogger(app.config['LOGGER_NAME'])
    logger.info("App created")
    app.app_context().push()
    logger.info("App context pushed")

    logger.info("Configuring mongo db skeleton")
    # create mongo db skeleton
    mongo_client = get_mongo_client(app.config['MONGO_CONNECT_DICT'], tls_flag=False, tlsAllowInvalidCertificates=True)
    # It's OK to hardcode here - this run context is for dev/demo only anyway
    create_project.run(mongo_client, 
                       app.config['DB_NAME'],
                       app.config['USER_COLLECTION_NAME'],
                       app.config['PROJECT_COLLECTION_NAME'],
                       app.config['PROJECT_DATA_COLLECTION_NAME'],
                       json_data_dir="example_database/default")

    logger.info("Running App")
    app.run(debug=True,
            host='0.0.0.0',
            port=5001,
            extra_files=chain(Path.cwd().joinpath('app/templates').rglob('*.html'),
                                Path.cwd().joinpath('app/static/styles').rglob('*.css'))
            )