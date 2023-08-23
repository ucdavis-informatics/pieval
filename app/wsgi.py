from flask import Flask
import logging
from logging.handlers import TimedRotatingFileHandler

from app import pieval

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

    # add auth
    # logger.info("Configuring OIDC auth layer")
    # auth.oidc.init_app(app)

    # register blueprints
    logger.info("Registerting blueprints")
    app.register_blueprint(pieval.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
    # app.register_blueprint(auth.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
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

