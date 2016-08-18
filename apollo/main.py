import os
import logging

from flask import Flask, jsonify, g
from apollo.common.database import init_db
from apollo.components.user.models import User


def setup_logging():
    # logging
    stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.WARNING)
    verbose = '%(levelname)s %(asctime)s %(name)s %(funcName)s:%(lineno)s] %(message)s'
    stream_handler.setFormatter(logging.Formatter(verbose))
    logger = logging.getLogger("pluto")
    logger.addHandler(stream_handler)
    if os.getenv('ENV') != 'production':
        logger.setLevel(logging.DEBUG)

    #  TODO Error Mails
    # http://flask.pocoo.org/docs/0.10/errorhandling/
    # app.logger.addHandler(stream_handler)


def create_app():
    """
    Factory to set up the application
    # http://flask.pocoo.org/docs/0.10/patterns/appfactories/
    :return:
    """
    app = Flask(__name__)
    if os.getenv('ENV') != 'production':
        app.config['DEBUG'] = True
    app.secret_key = os.getenv('SECRET_KEY')
    # register logging
    setup_logging()
    return app

app = create_app()


@app.route('/', endpoint='index')
def index():
    return jsonify({'data': 'Hello apollo'}), 200


@app.errorhandler(404)
def not_found(error=None):
    from flask import request
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    return jsonify(message), 404


# --------------
# Database
# --------------
@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db(models=[User])
    print('Initialized the database.')


@app.teardown_appcontext
def close_db(exception=None):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.shutdown()
