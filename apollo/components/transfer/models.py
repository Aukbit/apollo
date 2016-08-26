import uuid
from datetime import datetime, timedelta
import time
import simplejson as json
import urllib
from google.appengine.api import modules
from google.appengine.api import taskqueue
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from transitions import Machine
from flask import url_for
from .custom_types import Amount
from .general import (TRANSFER_CREATED,
                      TRANSFER_STATUS_MAP,
                      TRANSFER_STATUS_STRING_MAP,
                      TRANSFER_STATUS_STRING_CHOICES,
                      TRANSFER_STATE_TRANSITIONS)
from .exceptions import (AccountTransactionNotAvailable,
                         DestinationTransactionNotAvailable,
                         UserNotAvailable,
                         ReasonNotAvailable)
from .custom_types import Task
from ..account.models import (CurrentAccount,
                              DebitAccountTransaction,
                              CreditAccountTransaction)
from ...common.responses import Response
from ...common.abstract.models import AbstractBaseModel
from ...common.failure_codes import (FAILURE_INSUFFICIENT_FUNDS,
                                     FAILURE_INVALID_ACCOUNT_SIGNATURE,
                                     FAILURE_INVALID_DESTINATION_SIGNATURE,
                                     FAILURE_INVALID_ACCOUNT_OPERATION_ERROR,
                                     FAILURE_INVALID_DESTINATION_OPERATION_ERROR)
from ...common.mixins.task_queue import TaskQueueMixin
from ...common.mixins.state_machine import MachineMixin


class Transfer(AbstractBaseModel, TaskQueueMixin, MachineMixin):
    """
    Transfer
    """
    __table_name__ = 'transfer'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    description = columns.Text()
    value = columns.UserDefinedType(Amount, required=True)
    account_id = columns.UUID(required=True)
    destination_id = columns.UUID(required=True)
    # signatures
    signatures = columns.Map(columns.Text, columns.Text)
    #
    type = columns.Text(discriminator_column=True)
    status = columns.TinyInt(default=TRANSFER_CREATED[0])
    # reverse
    reversed = columns.Boolean(default=False)
    value_reversed = columns.UserDefinedType(Amount)
    # failure
    failure_code = columns.SmallInt()
    # cancel reason
    cancel_user_id = columns.UUID()
    cancel_reason = columns.Text()
    # tasks
    tasks = columns.Map(columns.Text, columns.Text)

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

    def _is_txn_valid(self, txn=None):
        return txn is not None and self.id == txn.source_id

    def _get_act_txn(self, event):
        act_txn = event.kwargs.get('act_txn')
        if self._is_txn_valid(act_txn):
            return act_txn

        act_txn = DebitAccountTransaction.objects.filter(account_id=self.account_id).get()
        if self._is_txn_valid(act_txn):
            return act_txn

        if act_txn is None:
            raise AccountTransactionNotAvailable

    def _get_dst_txn(self, event):
        dst_txn = event.kwargs.get('dst_txn')
        if self._is_txn_valid(dst_txn):
            return dst_txn

        dst_txn = CreditAccountTransaction.objects.filter(account_id=self.destination_id).get()
        if self._is_txn_valid(dst_txn):
            return dst_txn

        if dst_txn is None:
            raise DestinationTransactionNotAvailable

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
        act_txn = self._get_act_txn(event)
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
        dst_txn = self._get_dst_txn(event)
        if dst_txn.is_succeed():
            return True
        if dst_txn.is_failed():
            self.failure_code = FAILURE_INVALID_ACCOUNT_OPERATION_ERROR[0]
        return False

    def has_failure_code(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.failure_code is not None

    def set_user(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        user = event.kwargs.get('user')
        if user is None:
            raise UserNotAvailable

        self.cancel_user_id = user.id

    def set_reason(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        reason = event.kwargs.get('reason')
        if reason is None:
            raise ReasonNotAvailable

        self.cancel_reason = reason

    def has_cancel_fields(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.cancel_reason is not None and self.cancel_user_id is not None

    # ---------------
    # Task Methods
    # ---------------
    def create_task_to_cancel_transfer(self):
        kwargs = dict()
        action = 'cancel'
        url_params = {'id': self.id, 'action': action}
        url = url_for('tasks.transfer_actions', **url_params)
        kwargs['queue_name'] = self.__table_name__
        kwargs['method'] = 'POST'
        kwargs['url'] = url
        kwargs['eta'] = datetime.utcnow() + timedelta(hours=24)
        kwargs['payload'] = urllib.urlencode({'action': action})
        # context['target'] = modules.get_current_module_name()
        task = self.add_task(**kwargs)
        if isinstance(task, taskqueue.Task):
            self.tasks['cancel'] = task.name


class P2pTransfer(Transfer):
    """
    P2pTransfer
    """
    __discriminator_value__ = 'p2p'

    def __init__(self, **values):
        super(P2pTransfer, self).__init__(**values)
        self.type = self.__discriminator_value__

    def _execute_txn(self, txn=None, persist=False):
        if self._is_txn_valid(txn):
            txn.go_execute(transfer=self, persist=persist)
            return txn

    def _cancel_txn(self, txn=None, persist=False):
        if self._is_txn_valid(txn):
            txn.go_cancel(transfer=self, persist=persist)
            return txn

    def _has_txn_funds(self, txn=None):
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
        act_txn = self._get_act_txn(event)
        if self._has_txn_funds(act_txn):
            act_txn = self._execute_txn(act_txn, persist)
            event.kwargs.update({'act_txn': act_txn})
            #
            dst_txn = self._get_dst_txn(event)
            dst_txn = self._execute_txn(dst_txn, persist)
            event.kwargs.update({'dst_txn': dst_txn})

    def execute_cancel(self, event, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        persist = event.kwargs.get('persist', False)
        #
        act_txn = self._get_act_txn(event)
        act_txn = self._cancel_txn(act_txn, persist)
        event.kwargs.update({'act_txn': act_txn})
        #
        dst_txn = self._get_dst_txn(event)
        dst_txn = self._cancel_txn(dst_txn, persist)
        event.kwargs.update({'dst_txn': dst_txn})