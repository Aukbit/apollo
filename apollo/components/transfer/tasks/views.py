import logging
logger = logging.getLogger(__name__)

from flask import (jsonify, request, url_for, Response)
from flask.views import MethodView

from flask import Blueprint
blueprint_tasks = Blueprint('transfers', __name__, url_prefix='/tasks')

from .shemas import ActionSchema


# API using Method View directly from Flask
# http://flask.pocoo.org/docs/0.10/views/


class TransferActions(MethodView):
    """
    TransferActions
    """
    schema = ActionSchema()

    def post(self, *args, **kwargs):
        """
        Process task
        curl -u token:empty -i -X POST -H "Content-Type: application/json" -d
        '{"title": "campaign"}' http://localhost:8080/api/v1/campaigns/

        Note: tasqueue sends encoded body as 'application/x-www-form-urlencoded'
        or 'application/octet-stream' which flask does not recognize
        :return:
        """

        if request.content_type == 'application/x-www-form-urlencoded':
            print request.form
            # data, errors = self.schema_action.load(request.form)
        elif request.content_type == 'application/octet-stream':
            import urlparse
            data_parsed = dict(urlparse.parse_qsl(request.data))
            print data_parsed

        return jsonify({'data': 'ok'}), 200

blueprint_tasks.add_url_rule('/transfers/<string:id>/actions/<string:action>',
                             view_func=TransferActions.as_view('transfer_actions'),
                             methods=['POST'],
                             endpoint='transfer_actions')
