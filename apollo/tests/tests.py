
import unittest2 as unittest

from flask import url_for
from main import app


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # request Flak context
        self.ctx = app.test_request_context()
        self.ctx.push()
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        self.ctx.pop()

    def test_endpoint(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(url_for('index'), '/')

