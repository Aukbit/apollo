import logging
logger = logging.getLogger(__name__)
import simplejson as json
from datetime import datetime, timedelta
import urllib
from google.appengine.api import modules
from flask import url_for
from ...common.subscriber import Subscriber


class TransferSubscriber(Subscriber):

    def on_event(self, sender, **kwargs):
        super(TransferSubscriber, self).on_event(sender, **kwargs)
        event = kwargs.get('instance', None)
        transfer = kwargs.get('parent', None)
        if event is not None and transfer is not None:
            transfer.create_expired_task()

transfer_subscriber = TransferSubscriber(senders=['event.transfer.created'])
