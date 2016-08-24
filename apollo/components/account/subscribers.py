import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import (CurrentAccount,
                     DebitAccountTransaction,
                     CreditAccountTransaction)
from .custom_types import Operation
from .general import TRANSACTION_CREATED
from ...common.subscriber import Subscriber


class UserSubscriber(Subscriber):

    @staticmethod
    def create_current_account(user):
        account_name = '{} current account'.format(user.username)
        CurrentAccount.create(owner_id=user.id,
                              name=account_name)

    def on_event(self, sender, **kwargs):
        super(UserSubscriber, self).on_event(sender, **kwargs)
        event = kwargs.get('instance', None)
        user = kwargs.get('parent', None)
        if event is not None and user is not None:
            self.create_current_account(user)

user_subscriber = UserSubscriber(senders=['event.user.created'])


class AccountTransactionSubscriber(Subscriber):

    @staticmethod
    def add_pending_transaction(event, account_transaction):
        account = CurrentAccount.objects(id=account_transaction.account_id).get()
        operation = dict()
        operation[account_transaction.id] = Operation(value=account_transaction.value,
                                                      type=account_transaction.type)
        account.pending.update(operation)
        account.save()

    def on_event(self, sender, **kwargs):
        super(AccountTransactionSubscriber, self).on_event(sender, **kwargs)
        event = kwargs.get('instance', None)
        account_transaction = kwargs.get('parent', None)
        if event is not None and account_transaction is not None and account_transaction.status == TRANSACTION_CREATED[0]:
            self.add_pending_transaction(event, account_transaction)

account_transaction_subscriber = AccountTransactionSubscriber(senders=['event.account_transaction.created'])


class TransferSubscriber(Subscriber):

    @staticmethod
    def create_debit_account_transaction(event, transfer):
        description = '{} debit transfer'.format(transfer.type)
        dat = DebitAccountTransaction.create(account_id=transfer.account_id,
                                             description=description,
                                             value=transfer.value,
                                             source_id=transfer.id)
        print dat

    @staticmethod
    def create_credit_account_transaction(event, transfer):
        description = '{} credit transfer'.format(transfer.type)
        cat = CreditAccountTransaction.create(account_id=transfer.destination_id,
                                              description=description,
                                              value=transfer.value,
                                              source_id=transfer.id)
        print cat

    def on_event(self, sender, **kwargs):
        super(TransferSubscriber, self).on_event(sender, **kwargs)
        event = kwargs.get('instance', None)
        transfer = kwargs.get('parent', None)
        if event is not None and transfer is not None:
            self.create_debit_account_transaction(event, transfer)
            self.create_credit_account_transaction(event, transfer)

transfer_subscriber = TransferSubscriber(senders=['event.transfer.created'])
