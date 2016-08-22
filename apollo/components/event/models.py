import uuid
from datetime import datetime
import time
import simplejson as json
from blinker import signal
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from .general import ACTIONS_MAP


class Event(Model):
    """
    Event
    """
    __table_name__ = 'event'

    parent_id = columns.UUID(primary_key=True)
    id = columns.TimeUUID(primary_key=True, clustering_order='DESC', default=uuid.uuid1)
    source_type = columns.Text(discriminator_column=True)
    action = columns.TinyInt()
    data = columns.Text(required=True)
    created_on = columns.DateTime(default=datetime.utcnow)

    @classmethod
    def create(cls, **kwargs):
        parent = kwargs.get('parent')
        if parent is None:
            raise ValidationError('parent - None values are not allowed.')

        kwargs['parent_id'] = parent.id
        kwargs['data'] = parent.to_json()
        del kwargs['parent']
        event = super(Event, cls).create(**kwargs)
        sender = 'event.{}'.format(event.type)
        signal('on_event').send(sender, instance=event, parent=parent)
        return event

    @property
    def type(self):
        data = json.loads(self.data)
        return '{}.{}'.format(data.get('object', 'object'), ACTIONS_MAP[self.action])


class EventApi(Event):
    """
    EventApi
    """
    __discriminator_value__ = 'api'
    log_id = columns.UUID()


class EventBot(Event):
    """
    EventBot
    """
    __discriminator_value__ = 'bot'

