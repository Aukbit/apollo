import uuid
from datetime import datetime
import time
import simplejson as json
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from .general import ACTIONS_MAP


class Event(Model):
    """
    Event
    """
    __table_name__ = 'event'

    id = columns.TimeUUID(primary_key=True, clustering_order="DESC", default=time.time)
    parent_id = columns.UUID(primary_key=True)
    source_type = columns.Text(discriminator_column=True)
    action = columns.TinyInt()
    data = columns.Text()
    created_on = columns.DateTime(default=datetime.utcnow)

    @property
    def type(self):
        print self.data
        return '{}.{}'.format('object', ACTIONS_MAP[self.action])


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

