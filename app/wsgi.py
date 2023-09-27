"""
Author: Bill Riedl
Date: 2023-09-27
Purpose: Entry point into pieval app
"""

from itertools import chain
import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask

# siblings
try:
    from app import pieval
except ModuleNotFoundError:
    import pieval
try:
    from app import data_loader
except ModuleNotFoundError:
    import data_loader
try:
    from app import build_mongo_db
except ModuleNotFoundError:
    import build_mongo_db

def create_app():
    # CREATE APP OBJECT
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    # initialize data loader

    # set up logger
    logger = logging.getLogger(app.config['LOGGER_NAME'])
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logger.setLevel(logging.DEBUG)

    fh = TimedRotatingFileHandler(app.config['LOGFILE_LOCATION'], when="midnight", interval=1, encoding='utf8')
    fh.suffix = "%Y-%m-%d"
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("Logger Configured")

    logger.info("Registering which auth mode the app is in: ")
    app.config['AUTH_ENABLED'] = os.environ.get('AUTH_ENABLED')
    logger.info("App AUTH MODE is %s", app.config['AUTH_ENABLED'])

    # register blueprints
    logger.info("Registerting blueprints")
    app.register_blueprint(pieval.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
    app.secret_key = app.config['SECRET_KEY']

    # initialize logger(s) in app files with logger name so they all get a handle to the same logger
    logger.info("Initializing logging in each module")
    pieval.init_logging(app.config['LOGGER_NAME'])

    # initialize data loader in pieval
    pieval.init_pv_dl(app.config['MONGO_CONNECT_DICT'],
                      app.config['DB_NAME'],
                      app.config['USER_COLLECTION_NAME'],
                      app.config['PROJECT_COLLECTION_NAME'],
                      app.config['PROJECT_DATA_COLLECTION_NAME'],
                      logger=logger)

    return app


def main():
    # DEVELOPMENT (Internal-facing, Debug on)
    os.environ['FLASK_ENV']='development'

    app = create_app()
    logger = logging.getLogger(app.config['LOGGER_NAME'])
    logger.info("App created")
    app.app_context().push()
    logger.info("App context pushed")

    logger.info("Configuring mongo db skeleton")
    # create mongo db skeleton
    mongo_client = data_loader.get_mongo_client(app.config['MONGO_CONNECT_DICT'], tls_flag=False, tlsAllowInvalidCertificates=True)
    build_mongo_db.run(mongo_client)

    logger.info("Running App")
    app.run(debug=True,
            host='0.0.0.0',
            port=5001,
            extra_files=chain(Path.cwd().joinpath('app/templates').rglob('*.html'),
                                Path.cwd().joinpath('app/static/styles').rglob('*.css'))
            )

if __name__ == '__main__':
    main()
