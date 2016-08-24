
import datetime
import base64

from mock import MagicMock, Mock, patch
from flask import request, g, url_for
from transitions import MachineError
from cassandra.cqlengine.management import drop_table
from apollo.common.database import init_db, get_db
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.user.models import User, Profile
from apollo.components.user.decorators import deco_auth_user
from apollo.components.event.models import Event, EventApi, EventBot
from apollo.components.event.general import ACTIONS_MAP, CREATED, UPDATED
from apollo.components.account.models import (CurrentAccount,
                                              AccountTransaction,
                                              DebitAccountTransaction,
                                              CreditAccountTransaction)
from apollo.components.account.general import (TRANSACTION_CREATED,
                                               TRANSACTION_SEALED,
                                               TRANSACTION_SUCCEED,
                                               TRANSACTION_CANCELLED,
                                               TRANSACTION_FAILED)
from apollo.components.transfer.models import P2pTransfer
from apollo.components.transfer.custom_types import Amount
from apollo.components.transfer.general import (TRANSFER_CREATED,
                                                TRANSFER_PENDING,
                                                TRANSFER_SUCCEED,
                                                TRANSFER_CANCELLED,
                                                TRANSFER_FAILED)
from apollo.common.currencies import DEFAULT_CURRENCY
from apollo.common.failure_codes import (FAILURE_INSUFFICIENT_FUNDS,
                                         FAILURE_INVALID_SIGNATURE)


class EventTestCase(TestAppEngineMixin):

    def setUp(self):
        super(EventTestCase, self).setUp()
        init_db(models=[P2pTransfer, DebitAccountTransaction, CreditAccountTransaction, CurrentAccount, EventApi, EventBot, User])
        self.db = get_db()

    def tearDown(self):
        super(EventTestCase, self).tearDown()
        drop_table(EventApi)
        drop_table(EventBot)
        drop_table(User)
        drop_table(CurrentAccount)
        drop_table(DebitAccountTransaction)
        drop_table(CreditAccountTransaction)
        drop_table(P2pTransfer)

    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    @deco_auth_user(username="leia", email="test.leia.skywalker@aukbit.com", password="123456")
    def test_create_transfer(self, *args):
        # assert null
        self.assertEqual(P2pTransfer.objects.count(), 0)
        self.assertEqual(AccountTransaction.objects.count(), 0)
        # get accounts
        account = CurrentAccount.objects.filter(owner_id=self.luke.id).get()
        destination = CurrentAccount.objects.filter(owner_id=self.leia.id).get()
        # assert accounts are empty
        self.assertEqual(account.available.amount, 0)
        self.assertEqual(destination.available.amount, 0)
        # add initial amount to account
        account.available.amount = 10000
        account.save()
        self.assertEqual(account.available.amount, 10000)
        #
        # create transfer
        #
        t = P2pTransfer.create(account_id=account.id,
                               destination_id=destination.id,
                               description='last dinner bill',
                               value=Amount(amount=500, currency=DEFAULT_CURRENCY[0]))
        self.assertIsNotNone(t.id)
        # assert transfer state machine
        self.assertEqual(len(t.machine.events), 3)
        self.assertEqual(len(t.machine.states), 5)
        self.assertEqual(t.state, TRANSFER_PENDING[1])
        #
        self.assertEqual(t.account_id, account.id)
        self.assertEqual(t.destination_id, destination.id)
        self.assertEqual(t.description, 'last dinner bill')
        self.assertEqual(t.value.amount, 500)
        self.assertEqual(t.value.currency, DEFAULT_CURRENCY[0])
        self.assertEqual(t.type, 'p2p')
        self.assertEqual(t.status, TRANSFER_PENDING[0])
        # reverse
        self.assertEqual(t.reversed, False)
        self.assertEqual(t.value_reversed, None)
        # assert is saved
        self.assertEqual(P2pTransfer.objects.count(), 1)
        # event
        self.assertEqual(Event.objects.filter(parent_id=t.id).count(), 1)
        # get transactions
        self.assertEqual(AccountTransaction.objects.count(), 2)
        #
        # get debit transaction
        #
        dat = DebitAccountTransaction.objects.filter(account_id=account.id).get()
        self.assertIsNotNone(dat.id)
        # assert transaction state machine
        self.assertEqual(len(dat.machine.events), 3)
        self.assertEqual(len(dat.machine.states), 5)
        self.assertEqual(dat.state, TRANSACTION_CREATED[1])
        #
        self.assertEqual(dat.description, 'p2p debit transfer')
        self.assertEqual(dat.value.amount, 500)
        self.assertEqual(dat.value.currency, DEFAULT_CURRENCY[0])
        self.assertEqual(dat.source_id, t.id)
        self.assertEqual(dat.status, TRANSACTION_CREATED[0])
        self.assertEqual(dat.type, 'debit')
        # assert fail transitions from this state
        with self.assertRaises(MachineError):
            dat.go_execute()
        # sign and seal debit account transaction
        dat.go_sign_and_seal(signature='signature')
        self.assertEqual(dat.status, TRANSACTION_SEALED[0])

        #
        # get credit transaction
        #
        cat = CreditAccountTransaction.objects.filter(account_id=destination.id).get()
        self.assertIsNotNone(cat.id)
        # assert transaction state machine
        self.assertEqual(len(cat.machine.events), 3)
        self.assertEqual(len(cat.machine.states), 5)
        self.assertEqual(cat.state, TRANSACTION_CREATED[1])
        #
        self.assertEqual(cat.description, 'p2p credit transfer')
        self.assertEqual(cat.value.amount, 500)
        self.assertEqual(cat.value.currency, DEFAULT_CURRENCY[0])
        self.assertEqual(cat.source_id, t.id)
        self.assertEqual(cat.status, TRANSACTION_CREATED[0])
        self.assertEqual(cat.type, 'credit')
        with self.assertRaises(MachineError):
            cat.go_execute()
        # sign and seal debit account transaction
        cat.go_sign_and_seal(signature='signature')
        self.assertEqual(cat.status, TRANSACTION_SEALED[0])
        #
        # get accounts
        #
        account = CurrentAccount.objects.filter(owner_id=self.luke.id).get()
        destination = CurrentAccount.objects.filter(owner_id=self.leia.id).get()
        # assert available funds
        self.assertEqual(account.available.amount, 9500)
        self.assertEqual(account.available.currency, DEFAULT_CURRENCY[0])
        self.assertEqual(destination.available.amount, 500)
        self.assertEqual(destination.available.currency, DEFAULT_CURRENCY[0])
        # assert pending operations
        self.assertEqual(len(account.pending), 0)
        self.assertEqual(len(destination.pending), 0)
        # assert fail transitions from this state
        with self.assertRaises(MachineError):
            t.go_transfer()
        with self.assertRaises(MachineError):
            t.go_cancel()

    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    @deco_auth_user(username="leia", email="test.leia.skywalker@aukbit.com", password="123456")
    def test_create_transfer_failure_insufficient_funds(self, *args):
        # assert
        self.assertEqual(P2pTransfer.objects.count(), 0)
        # get accounts
        account = CurrentAccount.objects.filter(owner_id=self.luke.id).get()
        destination = CurrentAccount.objects.filter(owner_id=self.leia.id).get()
        # assert accounts are empty
        self.assertEqual(account.available.amount, 0)
        self.assertEqual(destination.available.amount, 0)
        # create transfer
        t = P2pTransfer.create(account_id=account.id,
                               destination_id=destination.id,
                               description='last dinner bill',
                               value=Amount(amount=500, currency=DEFAULT_CURRENCY[0]))
        self.assertIsNotNone(t.id)
        # assert state machine
        self.assertEqual(len(t.machine.events), 2)
        self.assertEqual(len(t.machine.states), 4)
        #
        self.assertEqual(t.status, TRANSFER_FAILED[0])
        self.assertEqual(t.failure_code, FAILURE_INSUFFICIENT_FUNDS[0])
        # get accounts
        account = CurrentAccount.objects.filter(owner_id=self.luke.id).get()
        destination = CurrentAccount.objects.filter(owner_id=self.leia.id).get()
        # assert available funds
        self.assertEqual(account.available.amount, 0)
        self.assertEqual(destination.available.amount, 0)
        # assert pending operations
        self.assertEqual(len(account.pending), 1)
        self.assertEqual(len(destination.pending), 1)
        # assert fail transitions from this state
        with self.assertRaises(MachineError):
            t.go_transfer()

        #
        t.go_cancel()
