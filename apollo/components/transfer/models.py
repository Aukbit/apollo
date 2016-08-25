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
from .exceptions import (AccountTransactionNotAvailable,
                         DestinationTransactionNotAvailable)
from ..account.models import (CurrentAccount)
from ...common.responses import Response
from ...common.abstract.models import AbstractBaseModel
from ...common.failure_codes import (FAILURE_INSUFFICIENT_FUNDS,
                                     FAILURE_INVALID_ACCOUNT_SIGNATURE,
                                     FAILURE_INVALID_DESTINATION_SIGNATURE,
                                     FAILURE_INVALID_ACCOUNT_OPERATION_ERROR,
                                     FAILURE_INVALID_DESTINATION_OPERATION_ERROR)


class Transfer(AbstractBaseModel):
    """
    Transfer
    """
    __table_name__ = 'transfer'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    description = columns.Text()
    value = columns.UserDefinedType(Amount, required=True)
    account_id = columns.UUID(required=True)
    destination_id = columns.UUID(required=True)
    #
    signatures = columns.Map(columns.Text, columns.Text)
    #
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
        persist = event.kwargs.get('persist', False)
        if persist:
            self.save()

    def create_debit_account_transaction(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass
        # description = '{} debit transfer'.format(self.type)
        # dat = DebitAccountTransaction.create(account_id=self.account_id,
        #                                      description=description,
        #                                      value=self.value,
        #                                      source_id=self.id)
        # event.kwargs.update({'debit_account_transaction': dat})

    def create_credit_account_transaction(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass
        # description = '{} credit transfer'.format(self.type)
        # cat = CreditAccountTransaction.create(account_id=self.destination_id,
        #                                       description=description,
        #                                       value=self.value,
        #                                       source_id=self.id)
        # event.kwargs.update({'credit_account_transaction': cat})

    def set_account_signature(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        act_signature = event.kwargs.get('act_signature')
        # TODO is signature valid
        if act_signature:
            self.signatures['act_signature'] = act_signature

    def set_destination_signature(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        dst_signature = event.kwargs.get('dst_signature')
        # TODO is signature valid
        if dst_signature:
            self.signatures['dst_signature'] = dst_signature

    def has_valid_account_signature(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        signature = self.signatures.get('act_signature')
        # TODO is signature valid
        if signature is not 'signature':
            self.failure_code = FAILURE_INVALID_ACCOUNT_SIGNATURE[0]
            return False
        return True

    def has_valid_destination_signature(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        signature = self.signatures.get('dst_signature')
        # TODO is signature valid
        if signature is not 'signature':
            self.failure_code = FAILURE_INVALID_DESTINATION_SIGNATURE[0]
            return False
        return True

    def has_transaction_account_succeed(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        act_txn = event.kwargs.get('act_txn')
        if act_txn is None:
            raise AccountTransactionNotAvailable
        if act_txn.is_succeed():
            return True
        if act_txn.is_failed():
            self.failure_code = FAILURE_INVALID_ACCOUNT_OPERATION_ERROR[0]
        return False

    def has_transaction_destination_succeed(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        dst_txn = event.kwargs.get('dst_txn')
        if dst_txn is None:
            raise DestinationTransactionNotAvailable
        if dst_txn.is_succeed():
            return True
        if dst_txn.is_failed():
            self.failure_code = FAILURE_INVALID_ACCOUNT_OPERATION_ERROR[0]
        return False

    def has_funds(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass
        # account = CurrentAccount.objects(id=self.account_id).get()
        # if account.net.amount <= 0:
        #     self.failure_code = FAILURE_INSUFFICIENT_FUNDS[0]
        #     return False
        # return True

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

    def __init__(self, **values):
        super(P2pTransfer, self).__init__(**values)
        self.type = self.__discriminator_value__

    def _execute_txn(self, txn=None, persist=False):
        if txn is None:
            raise AccountTransactionNotAvailable
        txn.go_execute(transfer=self, persist=persist)
        return txn

    def _is_txn_valid(self, txn=None):
        if txn is None:
            raise AccountTransactionNotAvailable
        return self.id == txn.source_id

    def _has_txn_funds(self, txn=None):
        if txn is None:
            raise AccountTransactionNotAvailable

        if self._is_txn_valid(txn):
            act = CurrentAccount.objects(id=txn.account_id).get()
            if act.has_funds:
                return True
            self.failure_code = FAILURE_INSUFFICIENT_FUNDS[0]
            return False

    def execute_operation(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        persist = event.kwargs.get('persist', False)
        # confirm if account has funds
        act_txn = event.kwargs.get('act_txn')
        if self._has_txn_funds(act_txn):
            act_txn = self._execute_txn(act_txn, persist)
            event.kwargs.update({'act_txn': act_txn})
            #
            dst_txn = event.kwargs.get('dst_txn')
            dst_txn = self._execute_txn(dst_txn, persist)
            event.kwargs.update({'dst_txn': dst_txn})
