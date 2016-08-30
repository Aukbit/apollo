import os
import datetime
import base64
import time
import simplejson as json

from flask import url_for, g
from mock import MagicMock, Mock, patch

import stripe

from mock import MagicMock, Mock, patch
from flask import request, g, url_for
from transitions import MachineError
from cassandra.cqlengine.management import drop_table

from apollo.common.database import init_db, get_db
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.user.models import User, Profile
from apollo.components.user.decorators import deco_auth_user
from apollo.components.payment.models import (PaymentProcessor,
                                              StripePaymentProcessor)


class PaymentProcessorTestCase(TestAppEngineMixin):

    def setUp(self):
        super(PaymentProcessorTestCase, self).setUp()

    def tearDown(self):
        super(PaymentProcessorTestCase, self).tearDown()

    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    def test_create_payment_processor(self):
        # get payment processors
        processors = StripePaymentProcessor.objects.all()
        self.assertEqual(len(processors), 1)
        self.assertIsNotNone(processors[0].id)
        self.assertEqual(processors[0].owner_id, self.luke.id)
        self.assertEqual(processors[0].type, 'stripe')
        self.assertIsNotNone(processors[0].ext_customer_id)
        self.assertIsNotNone(processors[0].ext_connect_account_id)
        #
        processors[0].remove_ext_customer_id()




