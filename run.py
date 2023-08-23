#!flask/bin/python
# Import app variable from our app package
import app.wsgi as wsgi
import socket
import time
import random
import logging
import os
from pathlib import Path
from itertools import chain
from docker_kc import config_keycloak

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
    app.app_context().push()
    app.run(debug=True,
            host='0.0.0.0',
            port=5001,
            extra_files=chain(Path.cwd().joinpath('app/templates').rglob('*.html'),
                                Path.cwd().joinpath('app/static/styles').rglob('*.css'))
            )
