import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import P2pTransfer
from ...common.subscriber import Subscriber


class TransferSubscriber(Subscriber):

    def on_event(self, sender, **kwargs):
        super(TransferSubscriber, self).on_save(sender, **kwargs)
        event = kwargs.get('instance', None)
        transfer = kwargs.get('parent', None)
        if event is not None and transfer is not None:
            transfer.go_transfer()


transfer_subscriber = TransferSubscriber(senders=['event.transfer.created'])
