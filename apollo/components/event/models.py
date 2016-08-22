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
    data = columns.Text()
    created_on = columns.DateTime(default=datetime.utcnow)

    @property
    def type(self):
        data = json.loads(self.data)
        return '{}.{}'.format(data.get('object', 'object'), ACTIONS_MAP[self.action])

    # --------------
    # Super Methods
    # --------------
    def save(self):
        self.changed_on = datetime.utcnow()
        sender = 'event.{}'.format(self.type)
        signal('on_save').send(sender, instance=self)
        return super(Event, self).save()


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

