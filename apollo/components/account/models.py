import logging
logger = logging.getLogger(__name__)
import uuid
import simplejson as json
from transitions import Machine
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model

from .custom_types import Amount, Operation, Transaction
from .general import (TRANSACTION_PENDING,
                      TRANSACTION_STATUS_MAP,
                      TRANSACTION_STATUS_STRING_MAP,
                      TRANSACTION_STATUS_STRING_CHOICES,
                      TRANSACTION_STATE_TRANSITIONS)
from .exceptions import TransferNotAvailable
from ...common.responses import Response
from ...common.abstract.models import AbstractBaseModel
from ...common.currencies import DEFAULT_CURRENCY
from ...common.failure_codes import (FAILURE_TRANSACTION_OPERATION_ERROR,
                                     FAILURE_TRANSFER_IS_NOT_SEALED,
                                     FAILURE_INSUFFICIENT_FUNDS)


class Account(AbstractBaseModel):
    """
    Account
    """
    __table_name__ = 'account'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    owner_id = columns.UUID(index=True)
    name = columns.Text()
    type = columns.Text(discriminator_column=True)


class CurrentAccount(Account):
    """
    CurrentAccount
    """
    __discriminator_value__ = 'current'
    available = columns.UserDefinedType(Amount)
    pending = columns.Map(columns.UUID, columns.UserDefinedType(Operation))

    # --------------
    # Super Methods
    # --------------
    def save(self):
        """
        Note: convert key UUID to <type 'str'> in self.pending
        """
        for o in self.pending:
            if isinstance(o, uuid.UUID):
                self.pending[o.__str__()] = self.pending.pop(o)
        return super(CurrentAccount, self).save()

    @classmethod
    def create(cls, **kwargs):
        kwargs['available'] = Amount(amount=0, currency=DEFAULT_CURRENCY[0])
        return super(CurrentAccount, cls).create(**kwargs)

    # --------------
    # Super Methods END
    # --------------

    # --------------
    # Properties
    # --------------
    @property
    def pending_debits(self):
        return sum([operation.value.amount for operation in self.pending.values() if operation.type == 'debit'])

    @property
    def pending_credits(self):
        return sum([operation.value.amount for operation in self.pending.values() if operation.type == 'credit'])

    @property
    def net(self):
        total = self.available.amount - self.pending_debits
        return Amount(amount=total, currency=self.available.currency)

    @property
    def balance(self):
        total = self.available.amount - self.pending_debits + self.pending_credits
        return Amount(amount=total, currency=self.available.currency)

    @property
    def has_funds(self):
        return self.net.amount >= 0

    # --------------
    # Properties END
    # --------------

    # --------------
    # Methods
    # --------------
    def _pop_pending(self, id=None):
        try:
            return self.pending.pop(id)
        except KeyError as e:
            logger.error('No pending operation found with key {}'.format(e))
            return Response(error=FAILURE_TRANSACTION_OPERATION_ERROR)

    def execute_pending(self, id=None):
        o = self._pop_pending(id)
        if isinstance(o, Response):
            return o
        # make transaction amount available
        self.available.update(o)
        return Response()

    def cancel_pending(self, id=None):
        o = self._pop_pending(id)
        if isinstance(o, Response):
            return o
        return Response()


class AccountTransaction(AbstractBaseModel):
    """
    AccountTransaction
    """
    __table_name__ = 'account_transaction'

    account_id = columns.UUID(primary_key=True)
    id = columns.TimeUUID(primary_key=True, clustering_order='DESC', default=uuid.uuid1)
    description = columns.Text()
    value = columns.UserDefinedType(Amount)
    source_id = columns.UUID()
    signature = columns.Text()
    type = columns.Text(discriminator_column=True)
    status = columns.TinyInt(default=TRANSACTION_PENDING[0], index=True)
    # failure code
    failure_code = columns.SmallInt()

    def __init__(self, *args, **kwargs):
        super(AccountTransaction, self).__init__(*args, **kwargs)
        self._init_machine()

    # ---------------
    # Machine Methods
    # ---------------
    def _init_machine(self, transitions=TRANSACTION_STATE_TRANSITIONS):
        """
        Method to hook a state machine to the instance
        """
        states = list(TRANSACTION_STATUS_STRING_CHOICES)
        self.machine = Machine(model=self, states=states, transitions=transitions,
                               auto_transitions=False, send_event=True,
                               initial=TRANSACTION_STATUS_MAP[self.status],
                               after_state_change='_state_changed')

    def _state_changed(self, event):
        """
        callback from state machine to change status on instance and persist
        :param event: EventData
        :return:
        """
        self.status = TRANSACTION_STATUS_STRING_MAP[event.state.name]
        persist = event.kwargs.get('persist', False)
        if persist:
            self.save()

    def execute_operation(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        transfer = event.kwargs.get('transfer')
        if transfer is None:
            raise TransferNotAvailable

        if transfer.is_sealed():
            account = CurrentAccount.objects(id=self.account_id).get()
            response = account.execute_pending(self.id)
            event.kwargs.update({'operation_response': response})
            account.save()
        else:
            event.kwargs.update({'operation_response': Response(error=FAILURE_TRANSFER_IS_NOT_SEALED)})

    def execute_cancel(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        transfer = event.kwargs.get('transfer')
        if transfer is None:
            raise TransferNotAvailable

        if transfer.is_created():
            account = CurrentAccount.objects(id=self.account_id).get()
            response = account.cancel_pending(self.id)
            event.kwargs.update({'operation_response': response})
            account.save()

    def has_execute_succeed(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        response = event.kwargs.get('operation_response')
        if not response.is_success:
            self.failure_code = response.error_code
            return False
        return True

    def has_failure_code(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        return self.failure_code is not None


class DebitAccountTransaction(AccountTransaction):
    """
    DebitAccountTransaction
    """
    __discriminator_value__ = 'debit'

    def __init__(self, **values):
        super(DebitAccountTransaction, self).__init__(**values)
        self.type = self.__discriminator_value__


class CreditAccountTransaction(AccountTransaction):
    """
    CreditAccountTransaction
    """
    __discriminator_value__ = 'credit'

    def __init__(self, **values):
        super(CreditAccountTransaction, self).__init__(**values)
        self.type = self.__discriminator_value__
