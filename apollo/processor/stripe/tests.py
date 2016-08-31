import os
from datetime import datetime, timedelta
import base64
import time
import simplejson as json

from flask import url_for, g
from mock import MagicMock, Mock, patch

import stripe

from apollo.tests.mixins import TestAppEngineMixin
from apollo.processor.stripe.mixins import StripeMixin
from apollo.processor.stripe.fixtures import (STRIPE_FAKE_CARD_MAST, STRIPE_FAKE_CARD_VISA)
from apollo.common.utils.helpers import random_hexdigit


class StripeMixinTestCase(TestAppEngineMixin):

    def setUp(self):
        super(StripeMixinTestCase, self).setUp()
        self.email = 'stripe.test.customer.{}@aukbit.com'.format(random_hexdigit())

    def tearDown(self):
        super(StripeMixinTestCase, self).tearDown()

    def test_create_customer(self):
        # assert create customer
        mixin = StripeMixin()
        kwargs = {'email': self.email}
        c = mixin.create_customer(**kwargs)
        self.assertEqual(c.get('object'), 'customer')
        self.assertIsNotNone(c.get('id'))
        self.assertEqual(c.get('email'), self.email)
        # delete from vault
        cu = stripe.Customer.retrieve(c.get('id'))
        response = cu.delete()
        self.assertEqual(response.deleted, True)

    def test_delete_customer(self):
        # assert delete customer
        mixin = StripeMixin()
        kwargs = {'email': self.email}
        c = mixin.create_customer(**kwargs)
        self.assertEqual(c.get('object'), 'customer')
        self.assertIsNotNone(c.get('id'))
        # delete from vault
        mixin.delete_customer(customer_id=c.get('id'))
        cu = stripe.Customer.retrieve(c.get('id'))
        self.assertEqual(cu.deleted, True)

    def test_get_or_create_customer(self):
        # assert can create a customer in vault, with Stripe fake card
        # https://stripe.com/docs/testing
        mixin = StripeMixin()
        kwargs = {'email': self.email}
        payment_method_nonce = STRIPE_FAKE_CARD_VISA
        c = mixin.get_or_create_customer(payment_method_nonce=payment_method_nonce, **kwargs)
        # print customer
        self.assertEqual(c.get('object'), 'customer')
        self.assertIsNotNone(c.get('id'))
        # assert sources
        self.assertIsNotNone(c.get('default_source'))
        self.assertIsNotNone(c.get('sources'))
        self.assertIsNotNone(c.get('sources').get('data'))
        self.assertEqual(len(c.get('sources').get('data')), 1)
        self.assertEqual(c.get('sources').get('data')[0].get('object'), 'card')
        self.assertIsNotNone(c.get('sources').get('data')[0].get('id'))
        self.assertIsNotNone(c.get('sources').get('data')[0].get('last4'))
        self.assertIsNotNone(c.get('sources').get('data')[0].get('exp_month'))
        self.assertIsNotNone(c.get('sources').get('data')[0].get('exp_year'))
        self.assertIsNotNone(c.get('sources').get('data')[0].get('brand'))
        # delete from vault
        cu = stripe.Customer.retrieve(c.get('id'))
        cu.delete()

    def test_create_account(self):
        # assert create customer
        mixin = StripeMixin()
        kwargs = {'email': self.email,
                  'country': 'GB',
                  'currency': 'GBP',
                  'first_name': 'first_name',
                  'last_name': 'last_name',
                  'dob': datetime.utcnow() - timedelta(days=9000),
                  'address': {'city': 'London', 'line1': 'line1', 'postal_code': 'W14'},
                  'tos_acceptance': {'date': datetime.utcnow(), 'ip': '127.0.0.1'}
                  }
        a = mixin.create_account(**kwargs)
        self.assertEqual(a.get('object'), 'account')
        self.assertIsNotNone(a.get('id'))
        self.assertEqual(a.get('email'), self.email)
        self.assertEqual(a.get('transfers_enabled'), False)
        self.assertEqual(len(a.get('verification').get('fields_needed')), 2)
        print 'test_create_account: fields_needed {}'.format(a.get('verification').get('fields_needed'))
        # delete from vault
        act = stripe.Account.retrieve(a.get('id'))
        response = act.delete()
        self.assertEqual(response.deleted, True)

    #
    # def test_get_or_create_connect_account(self):
    #     # assert create connect account
    #     mixin = StripeMixin()
    #     a = mixin.get_or_create_connect_account(managed=True)
    #     self.assertEqual(a.get('object'), 'account')
    #     self.assertIsNotNone(a.get('id'))
    #     # delete from vault
    #     ac = stripe.Account.retrieve(a.get('id'))
    #     ac.delete()
    #
    # def test_deauthorize_connect_account(self):
    #     # assert deauthorize connect account
    #     mixin = StripeMixin()
    #     # TODO
    #     self.assertTrue(True)
