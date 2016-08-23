import os
import logging

from flask import Flask, jsonify, g
from apollo.common.database import init_db
from apollo.components.user.models import User
from apollo.components.log.models import log_http_request, log_http_response


def setup_logging(debug=False):
    # logging
    stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.WARNING)
    verbose = '%(levelname)s %(asctime)s %(name)s %(funcName)s:%(lineno)s] %(message)s'
    stream_handler.setFormatter(logging.Formatter(verbose))
    logger = logging.getLogger("apollo")
    logger.addHandler(stream_handler)
    if debug:
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
    # Load default config
    app.config.update(
        DEBUG=True,
        SECRET_KEY='SECRET_KEY'
    )
    # Override config from an environment variable
    app.config.from_envvar('SETTINGS_PATH')
    if app.config.get('ENV') == 'production':
        app.config['DEBUG'] = False
    # register logging
    setup_logging(app.config.get('DEBUG'))
    return app

app = create_app()


@app.route('/', endpoint='index')
def index():
    return jsonify({'data': 'Hello apollo'}), 200


@app.before_request
def log_request():
    from flask import request
    log_http_request(request)


@app.after_request
def after_request(response):
    log_http_response(response)
    return response


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
