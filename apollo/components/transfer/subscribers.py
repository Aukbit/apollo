import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import P2pTransfer
from ...common.subscriber import Subscriber


class TransferSubscriber(Subscriber):

    # @staticmethod
    # def create_current_account(event):
    #     data = json.loads(event.data)
    #     account_name = '{} current account'.format(data.get('username'))
    #     CurrentAccount.create(owner_id=event.parent_id,
    #                           name=account_name)

    def on_event(self, sender, **kwargs):
        super(TransferSubscriber, self).on_save(sender, **kwargs)
        event = kwargs.get('instance', None)
        transfer = kwargs.get('parent', None)
        if event is not None and event.type == 'transfer.created' and transfer is not None:
            print transfer
            transfer.go_transfer()


transfer_subscriber = TransferSubscriber(senders=['event.transfer.created'])
