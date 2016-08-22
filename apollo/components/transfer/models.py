import uuid
from datetime import datetime
import time
import simplejson as json
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from transitions import Machine

from .custom_types import Amount
from .general import (TRANSFER_PENDING,
                      TRANSFER_STATUS_MAP,
                      TRANSFER_STATUS_STRING_MAP,
                      TRANSFER_STATUS_STRING_CHOICES,
                      TRANSFER_STATE_TRANSITIONS)
from ..account.models import (DebitAccountTransaction, CreditAccountTransaction)
from ...common.abstract.models import AbstractBaseModel


class Transfer(AbstractBaseModel):
    """
    Transfer
    """
    __table_name__ = 'transfer'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    account_id = columns.UUID(required=True)
    description = columns.Text()
    type = columns.Text(discriminator_column=True)
    status = columns.TinyInt(default=TRANSFER_PENDING[0])
    # reverse
    reversed = columns.Boolean(default=False)
    value_reversed = columns.UserDefinedType(Amount)

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
        callback from state machine to change status on instance
        :param event: EventData
        :return:
        """
        self.status = TRANSFER_STATUS_STRING_MAP[event.state.name]
        # self.save()

    def create_debit_account_transaction(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        description = '{} debit transfer'.format(self.type)
        DebitAccountTransaction.create(account_id=self.account_id,
                                       description=description,
                                       value=self.value,
                                       source_id=self.id)

    def create_credit_account_transaction(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        description = '{} credit transfer'.format(self.type)
        CreditAccountTransaction.create(account_id=self.account_id,
                                        description=description,
                                        value=self.value,
                                        source_id=self.id)

    def has_succeeded(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        print
        return True


class P2pTransfer(Transfer):
    """
    P2pTransfer
    """
    __discriminator_value__ = 'p2p'
    value = columns.UserDefinedType(Amount, required=True)
    destination_id = columns.UUID(required=True)

