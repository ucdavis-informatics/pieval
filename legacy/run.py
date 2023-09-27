#!flask/bin/python
# Import app variable from our app package
import app.wsgi as wsgi
import time
import random
import logging
import os
from pathlib import Path
from itertools import chain
from pymongo import MongoClient
import src.build_mongo_db as build_mongo_db

def create_app():
    time.sleep(random.uniform(0.2,1.5))
    app = wsgi.create_app()
    logger = logging.getLogger(app.config['LOGGER_NAME'])
    logger.info("Logger Configured")
    return app

def get_mongo_client(mongo_connect_dict, tls_flag=True, tlsAllowInvalidCertificates=False):
    return MongoClient(host=mongo_connect_dict['host'],
                               port=int(mongo_connect_dict['port']),
                               username=mongo_connect_dict['user'],
                               password=mongo_connect_dict['pass'],
                               authSource=mongo_connect_dict['auth_source'],
                               tls=tls_flag,
                               tlsAllowInvalidCertificates=tlsAllowInvalidCertificates)


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
    build_mongo_db.run(mongo_client)

    logger.info("Running App")
    app.run(debug=True,
            host='0.0.0.0',
            port=5001,
            extra_files=chain(Path.cwd().joinpath('app/templates').rglob('*.html'),
                                Path.cwd().joinpath('app/static/styles').rglob('*.css'))
            )
