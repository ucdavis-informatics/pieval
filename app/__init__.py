from flask import Flask
from flask_apscheduler import APScheduler
import socket

# CREATE APP OBJECT
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
from app import pieval

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
    print("!!!scheduler already started, DO NOTHING")
else:
    print("Starting Scheduler because it does not exist yet!")
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

app.register_blueprint(pieval.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
app.secret_key = app.config['SECRET_KEY']

