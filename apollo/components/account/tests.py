
import datetime
import base64

from mock import MagicMock, Mock, patch
from flask import request, g, url_for
from cassandra.cqlengine.management import drop_table
from cassandra.cqlengine import columns
from apollo.common.database import init_db, get_db
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.account.models import CurrentAccount
from apollo.components.user.models import User, Profile
from apollo.components.user.decorators import deco_auth_user
from apollo.components.event.models import Event, EventApi, EventBot
from apollo.common.currencies import DEFAULT_CURRENCY


class AccountTestCase(TestAppEngineMixin):

    def setUp(self):
        super(AccountTestCase, self).setUp()
        init_db(models=[CurrentAccount, EventApi, EventBot, User])
        self.db = get_db()

    def tearDown(self):
        super(AccountTestCase, self).tearDown()
        drop_table(EventApi)
        drop_table(EventBot)
        drop_table(User)
        drop_table(CurrentAccount)

    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    def test_create_account(self):
        # get accounts
        accounts = CurrentAccount.objects.all()
        self.assertEqual(len(accounts), 1)
        self.assertIsNotNone(accounts[0].id)
        self.assertEqual(accounts[0].owner_id, self.luke.id)
        self.assertEqual(accounts[0].name, '{} current account'.format(self.luke.username))
        self.assertEqual(accounts[0].available.amount, 0)
        self.assertEqual(accounts[0].available.currency, DEFAULT_CURRENCY[0])
        self.assertEqual(len(accounts[0].pending), 0)
        # assert event is created
        self.assertEqual(Event.objects.count(), 2)



