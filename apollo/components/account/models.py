import logging
logger = logging.getLogger(__name__)
import uuid
import simplejson as json
from transitions import Machine
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model

from .custom_types import Amount, Operation, Transaction
from .general import (TRANSACTION_CREATED,
                      TRANSACTION_STATUS_MAP,
                      TRANSACTION_STATUS_STRING_MAP,
                      TRANSACTION_STATUS_STRING_CHOICES,
                      TRANSACTION_STATE_TRANSITIONS)
from ...common.abstract.models import AbstractBaseModel
from ...common.currencies import DEFAULT_CURRENCY
from ...common.failure_codes import FAILURE_INVALID_SIGNATURE


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

    # --------------
    # Properties END
    # --------------

    # --------------
    # Methods
    # --------------
    def execute_pending(self, uuid=None):
        try:
            o = self.pending.pop(uuid)
            self.available.update(o)
            self.save()
            return True
        except KeyError as e:
            logger.error('No pending operation found with key {}'.format(e))
            return False


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
    status = columns.TinyInt(default=TRANSACTION_CREATED[0], index=True)
    # failure code
    failure_code = columns.SmallInt()
    # cancel reason
    cancel_reason = columns.Text()

    def __init__(self, *args, **kwargs):
        super(AccountTransaction, self).__init__(*args, **kwargs)
        self._init_machine()

    # ---------------
    # Machine Methods
    # ---------------
    def _init_machine(self):
        """
        Method to hook a state machine to the instance
        """
        states = list(TRANSACTION_STATUS_STRING_CHOICES)
        transitions = TRANSACTION_STATE_TRANSITIONS
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

    def execute_operation(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        account = CurrentAccount.objects(id=self.account_id).get()
        result = account.execute_pending(self.id)
        event.kwargs.update({'result': result})

    def has_valid_signature(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        # TODO: validate signature method
        signature = event.kwargs.get('signature')
        if signature is not 'signature':
            self.failure_code = FAILURE_INVALID_SIGNATURE[0]
            return False
        return True

    def has_failure_code(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        return self.failure_code is not None

    def has_operation_succeed(self, event, **kwargs):
        """

        :param event: EventData
        :return:
        """
        return event.kwargs.get('result', False)


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
