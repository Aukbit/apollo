import logging
logger = logging.getLogger(__name__)
from google.appengine.ext import ndb

from .models import EventApi
from .general import CREATED, UPDATED
from ...components.log.models import LogHttpRequest
from ...common.subscriber import Subscriber


class EventSubscriber(Subscriber):

    @staticmethod
    def create_event(instance):
        from flask import g
        if isinstance(getattr(g, '_log', None), LogHttpRequest):
            if instance._is_persisted:
                action = UPDATED[0]
            else:
                action = CREATED[0]
            EventApi.create(parent_id=instance.id,
                            action=action,
                            data=instance.to_json(),
                            log_id=g._log.id)

    def on_save(self, sender, **kwargs):
        super(EventSubscriber, self).on_save(sender, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None:
            self.create_event(instance)


event_subscriber = EventSubscriber()
