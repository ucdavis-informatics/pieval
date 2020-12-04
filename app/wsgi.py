from flask import Flask
from flask_apscheduler import APScheduler
import socket
import logging
from logging.handlers import TimedRotatingFileHandler

from app import pieval, auth

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
    logger.info("Configuring OIDC auth layer")
    auth.oidc.init_app(app)

    # register blueprints
    logger.info("Registerting blueprints")
    app.register_blueprint(pieval.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
    app.register_blueprint(auth.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
    app.secret_key = app.config['SECRET_KEY']

    # initialize logger(s) in app files with logger name so they all get a handle to the same logger
    logger.info("Initializing logging in each module")
    pieval.init_logging(app.config['LOGGER_NAME'])
    auth.init_logging(app.config['LOGGER_NAME'])

    # initialize data loader in pieval
    pieval.init_pv_dl(app.config['DATASOURCE_TYPE'], app.config['DATASOURCE_LOCATION'], app.config['IMAGE_DIRECTORY'],
                      v_role_id=app.config['VAULT_ROLE_ID'],
                      v_sec_id=app.config['VAULT_SECRET_ID'],
                      v_server=app.config['VAULT_SERVER'],
                      db_schema=app.config['DB_SCHEMA'],
                      logger=logger)

    # start scheduler
    # with mega hack from SO that arbitrarily binds a socket as 'flag' to tell other workers
    # not to also create a scheduler - clever
    # Downsides - This relies on not needing this socket for something else
    # Also relies on GC to clean it up if it's not being used
    # https://stackoverflow.com/questions/16053364/make-sure-only-one-worker-launches-the-apscheduler-event-in-a-pyramid-web-app-ru
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47200))
    except socket.error:
        logger.info("--- Scheduler already started, DO NOTHING ---")
    else:
        logger.info("--- Starting Scheduler because it does not exist yet! ---")
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
    return app

