import uuid
from datetime import datetime
import time
import simplejson as json
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from transitions import Machine

from .custom_types import Amount
from .general import (TRANSFER_CREATED,
                      TRANSFER_STATUS_MAP,
                      TRANSFER_STATUS_STRING_MAP,
                      TRANSFER_STATUS_STRING_CHOICES,
                      TRANSFER_STATE_TRANSITIONS)
from ..account.models import (CurrentAccount,
                              DebitAccountTransaction,
                              CreditAccountTransaction)
from ...common.abstract.models import AbstractBaseModel
from ...common.failure_codes import FAILURE_INSUFFICIENT_FUNDS


class Transfer(AbstractBaseModel):
    """
    Transfer
    """
    __table_name__ = 'transfer'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    account_id = columns.UUID(required=True)
    description = columns.Text()
    type = columns.Text(discriminator_column=True)
    status = columns.TinyInt(default=TRANSFER_CREATED[0])
    # reverse
    reversed = columns.Boolean(default=False)
    value_reversed = columns.UserDefinedType(Amount)
    # failure
    failure_code = columns.SmallInt()

    def __init__(self, *args, **kwargs):
        super(Transfer, self).__init__(*args, **kwargs)
        self._init_machine()

    # ---------------
    # Machine Methods
    # ---------------
    def _init_machine(self):
        """
        Method to hook a state machine to the instance
        """
        states = list(TRANSFER_STATUS_STRING_CHOICES)
        transitions = TRANSFER_STATE_TRANSITIONS
        self.machine = Machine(model=self, states=states, transitions=transitions,
                               auto_transitions=False, send_event=True,
                               initial=TRANSFER_STATUS_MAP[self.status],
                               after_state_change='_state_changed')

    def _state_changed(self, event):
        """
        callback from state machine to change status on instance and persist
        :param event: EventData
        :return:
        """
        self.status = TRANSFER_STATUS_STRING_MAP[event.state.name]

    def create_debit_account_transaction(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        description = '{} debit transfer'.format(self.type)
        dat = DebitAccountTransaction.create(account_id=self.account_id,
                                             description=description,
                                             value=self.value,
                                             source_id=self.id)
        event.kwargs.update({'debit_account_transaction': dat})

    def create_credit_account_transaction(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        description = '{} credit transfer'.format(self.type)
        cat = CreditAccountTransaction.create(account_id=self.destination_id,
                                              description=description,
                                              value=self.value,
                                              source_id=self.id)
        event.kwargs.update({'credit_account_transaction': cat})

    def has_funds(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        account = CurrentAccount.objects(id=self.account_id).get()
        if account.net.amount <= 0:
            self.failure_code = FAILURE_INSUFFICIENT_FUNDS[0]
            return False
        return True

    def has_failure_code(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.failure_code is not None


class P2pTransfer(Transfer):
    """
    P2pTransfer
    """
    __discriminator_value__ = 'p2p'

    value = columns.UserDefinedType(Amount, required=True)
    destination_id = columns.UUID(required=True)

    def __init__(self, **values):
        super(P2pTransfer, self).__init__(**values)
        self.type = self.__discriminator_value__

    def execute_operation(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        #
        dat = event.kwargs.get('debit_account_transaction')
        if isinstance(dat, DebitAccountTransaction):
            if dat.go_available():
                dat.save()
        #
        cat = event.kwargs.get('credit_account_transaction')
        if isinstance(cat, CreditAccountTransaction):
            if cat.go_available():
                cat.save()
