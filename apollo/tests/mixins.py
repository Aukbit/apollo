import datetime
import logging
import sys
import os
import unittest2 as unittest

from cassandra.cqlengine import connection
from cassandra.cqlengine.management import drop_keyspace, create_keyspace_simple, drop_table
from webtest import TestApp
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import ndb
#
from apollo.tests.context import main
from apollo.common.database import init_db, get_db
from apollo.components.user.models import User
from apollo.components.log.models import LogHttpRequest
from apollo.components.event.models import (Event, EventApi, EventBot)
from apollo.components.account.models import (CurrentAccount,
                                              AccountTransaction,
                                              DebitAccountTransaction,
                                              CreditAccountTransaction)
from apollo.components.transfer.models import (Transfer,
                                               P2pTransfer)
from apollo.components.payment.models import (PaymentProcessor,
                                              StripePaymentProcessor)


class TestAppEngineMixin(unittest.TestCase):
    """
    Mixin to set up tests for app engine
    """
    @classmethod
    def setUpClass(cls):
        """
        initialization logic for the test suite declared in the test module
        code that is executed before all tests in one test run
        :return:
        """
        # request Flak context
        cls.ctx = main.app.test_request_context()
        # cls.ctx = app_watchdog.test_request_context()
        cls.ctx.push()
        # propagate the exceptions to the test client
        main.app.config['TESTING'] = True
        main.app.config['DATABASE_KEYSPACE'] = 'tests'
        connection.default()
        create_keyspace_simple('tests', 1)

    @classmethod
    def tearDownClass(cls):
        """
        clean up logic for the test suite declared in the test module
        code that is executed after all tests in one test run
        :return:
        """
        # drop_keyspace('tests')
        cls.ctx.pop()

    def setUp(self):
        """
        # initialization logic
        # code that is executed before each test
        :return:
        """
        # AppEngine Testbed
        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.setup_env(app_id='apollo-tests')
        self.testbed.activate()

        # Next, declare which service stubs you want to use.
        # Create a consistency policy that will simulate the High Replication consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)

        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_modules_stub()
        # https://cloud.google.com/appengine/docs/python/tools/localunittesting?hl=en#Python_Writing_task_queue_tests
        # https://cloud.google.com/appengine/docs/python/tools/localunittesting#Python_Writing_task_queue_tests
        root_path = os.path.join(os.path.dirname(__file__), '../../')
        # print root_path
        # Note: root_path must be the path of where queue.yaml remains
        self.testbed.init_taskqueue_stub(root_path=root_path)
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        # create a test server for us to prod
        self.testapp = TestApp(main.app)
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()
        #
        init_db(models=[User,
                        LogHttpRequest,
                        Event,
                        EventApi,
                        EventBot,
                        CurrentAccount,
                        DebitAccountTransaction,
                        CreditAccountTransaction,
                        Transfer,
                        P2pTransfer,
                        PaymentProcessor,
                        StripePaymentProcessor])
        self.db = get_db()

    def tearDown(self):
        drop_table(User)
        drop_table(LogHttpRequest)
        drop_table(Event)
        drop_table(EventApi)
        drop_table(EventBot)
        drop_table(CurrentAccount)
        drop_table(DebitAccountTransaction)
        drop_table(CreditAccountTransaction)
        drop_table(Transfer)
        drop_table(P2pTransfer)
        drop_table(PaymentProcessor)
        drop_table(StripePaymentProcessor)
        self.testbed.deactivate()

    def run_tasks(self, url=None, queue_name=None, method='POST', response_status_code=200, **kwargs):
        """
        Helper method to execute a specific group of tasks
        :param user:
        :param queue_name:
        :param queue_url:
        :param kwargs:
        :return:
        """
        from google.appengine.api import namespace_manager
        tasks = self.taskqueue_stub.get_filtered_tasks(url=url,
                                                       queue_names=[queue_name])
        for task in tasks:
            namespace = task.headers.get('X-AppEngine-Current-Namespace', '')
            previous_namespace = namespace_manager.get_namespace()
            try:
                namespace_manager.set_namespace(namespace)
                headers = {
                        k: v for k, v in task.headers.iteritems()
                        if k.startswith('X-AppEngine')}
                if method == 'PUT':
                    response = self.testapp.put(url, task.payload, headers=headers, status='*')
                else:
                    response = self.testapp.post(url, task.payload, headers=headers, status='*')
            finally:
                namespace_manager.set_namespace(previous_namespace)
