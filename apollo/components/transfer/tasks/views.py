import logging
logger = logging.getLogger(__name__)

from flask import (jsonify, request, url_for, Response)
from flask.views import MethodView

from flask import Blueprint
blueprint_tasks = Blueprint('tasks', __name__, url_prefix='/tasks/v1')

from .shemas import ActionSchema
from ..models import Transfer
from ....common.decorators import get_object


# API using Method View directly from Flask
# http://flask.pocoo.org/docs/0.10/views/


class TransferActions(MethodView):
    """
    TransferActions
    """
    schema = ActionSchema()

    @get_object(model=Transfer)
    def put(self, id, action, *args, **kwargs):
        """
        Process task
        curl -u token:empty -i -X POST -H "Content-Type: application/json" -d
        '{"title": "campaign"}' http://localhost:8080/api/v1/campaigns/

        Note: tasqueue sends encoded body as 'application/x-www-form-urlencoded'
        or 'application/octet-stream' which flask does not recognize
        :return:
        """
        data = {}
        if self.object and request.content_type == 'application/x-www-form-urlencoded':
            self.schema.context['instance'] = self.object
            data, errors = self.schema.load(request.form)
            if errors:
                return jsonify({'errors': errors}), 400

            kwargs['queue_name'] = request.headers.get('X-AppEngine-QueueName')
            kwargs['task_name'] = request.headers.get('X-AppEngine-TaskName')
            kwargs['persist'] = True
            metadata = data.get('metadata')
            if metadata:
                kwargs['reason'] = metadata.get('reason')

            if self.object.run_action(action, **kwargs):
                result = self.schema.dump(self.object)
                return jsonify({'data': result.data}), 200

        return jsonify({'data': data}), 400

blueprint_tasks.add_url_rule('/transfers/<string:id>/actions/<string:action>',
                             view_func=TransferActions.as_view('transfer_actions'),
                             methods=['PUT'],
                             endpoint='transfer_actions')
