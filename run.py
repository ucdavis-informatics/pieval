#!flask/bin/python
# Import app variable from our app package
import app.wsgi as wsgi
import socket
import time
import random
import logging

def create_app():
    time.sleep(random.uniform(0.2,1.5))
    app = wsgi.create_app()
    logger = logging.getLogger(app.config['LOGGER_NAME'])
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47201))
    except socket.error:
        logger.info("--- Neighboring services already started - DOING NOTHING ---")
    else:
        if app.config['RUN_MODE'] == 'dev':
            logger.info("------ Bringing App up in DEV mode!!! ----------")
            # here is where we should call the things that will 'autoconfigure' neighboring services with default params
            # KeyCloak
            logger.info("Auto configuring KeyCloak with dev/demo accounts")
            # Vault
            logger.info("Auto configuring Vault with dev/demo secrets - they aren't that secret in Dev mode!")
            # We DONT containerize our persistance layer
            # for dev use the filesystem based example database
    return app


if __name__ == '__main__':
    # DEVELOPMENT (Internal-facing, Debug on)
    app = create_app()
    app.app_context().push()
    app.run(debug=True, host='0.0.0.0', port=5001)
