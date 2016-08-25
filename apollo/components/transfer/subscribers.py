import logging
logger = logging.getLogger(__name__)
import simplejson as json

from ...common.subscriber import Subscriber


class TransferSubscriber(Subscriber):

    def on_event(self, sender, **kwargs):
        super(TransferSubscriber, self).on_event(sender, **kwargs)
        event = kwargs.get('instance', None)
        transfer = kwargs.get('parent', None)
        if event is not None and transfer is not None:
            print 'event.transfer.created'


transfer_subscriber = TransferSubscriber(senders=['event.transfer.created'])
