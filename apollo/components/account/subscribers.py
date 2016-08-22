import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import CurrentAccount
from .general import TRANSACTION_PENDING
from ...common.subscriber import Subscriber


class UserSubscriber(Subscriber):

    @staticmethod
    def create_current_account(user):
        account_name = '{} current account'.format(user.username)
        CurrentAccount.create(owner_id=user.id,
                              name=account_name)

    def on_event(self, sender, **kwargs):
        super(UserSubscriber, self).on_save(sender, **kwargs)
        event = kwargs.get('instance', None)
        user = kwargs.get('parent', None)
        if event is not None and event.type == 'user.created' and user is not None:
            self.create_current_account(user)

user_subscriber = UserSubscriber(senders=['event.user.created'])


class AccountTransactionSubscriber(Subscriber):

    @staticmethod
    def create_current_account(user):
        account_name = '{} current account'.format(user.username)
        CurrentAccount.create(owner_id=user.id,
                              name=account_name)

    def on_event(self, sender, **kwargs):
        super(AccountTransactionSubscriber, self).on_save(sender, **kwargs)
        event = kwargs.get('instance', None)
        at = kwargs.get('parent', None)
        if event is not None and at is not None and at.status == TRANSACTION_PENDING[0]:
            # self.create_current_account(user)
            print at
            a = CurrentAccount.objects(id=at.account_id).get()
            print a
            # a = at.account_id


account_transaction_subscriber = AccountTransactionSubscriber(senders=['event.account_transaction.created'])

