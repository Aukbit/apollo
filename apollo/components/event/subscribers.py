import logging
logger = logging.getLogger(__name__)

from .models import EventApi, EventBot
from .general import CREATED, UPDATED
from ...components.log.models import LogHttpRequest
from ...common.subscriber import Subscriber


class EventSubscriber(Subscriber):

    @staticmethod
    def create_event(instance):
        if instance._is_persisted:
            action = UPDATED[0]
        else:
            action = CREATED[0]

        from flask import g
        if isinstance(getattr(g, '_log', None), LogHttpRequest):
            log = g._log
            EventApi.create(parent=instance,
                            action=action,
                            log_id=log.id)
        else:
            EventBot.create(parent=instance,
                            action=action)

    def on_save(self, sender, **kwargs):
        super(EventSubscriber, self).on_save(sender, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None:
            self.create_event(instance)


event_subscriber = EventSubscriber(senders=['user',
                                            'account',
                                            'transfer'])
