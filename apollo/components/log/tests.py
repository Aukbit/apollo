
import datetime
import base64

from mock import MagicMock, Mock, patch
from flask import request, g, url_for
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.log.models import LogHttpRequest, Request, Response
from apollo.components.log.general import HTTP_METHODS_MAP, GET


class LogHttpRequestTestCase(TestAppEngineMixin):

    def setUp(self):
        super(LogHttpRequestTestCase, self).setUp()

    def tearDown(self):
        super(LogHttpRequestTestCase, self).tearDown()

    def test_index_endpoint(self):
        url = url_for('index')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_log_http_request(self):
        # assert 0
        self.assertEqual(LogHttpRequest.objects.count(), 0)
        # make request
        url = url_for('index')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
        # get log from global g
        self.assertTrue(hasattr(g, '_log'))
        l = g._log
        # assert
        self.assertIsInstance(l, LogHttpRequest)
        self.assertIsNotNone(l.id)
        self.assertEqual(l.type, 'http_request')
        # request
        self.assertEqual(l.request.machine, '')
        self.assertEqual(l.request.ip, None)
        self.assertEqual(l.request.content_type, None)
        self.assertEqual(l.request.content_body, '')
        self.assertEqual(HTTP_METHODS_MAP[l.request.method], GET[1])
        self.assertIsNotNone(l.request.headers)
        self.assertIsNotNone(l.request.request_on)
        # response
        self.assertEqual(l.response.content_type, 'application/json')
        self.assertIsNotNone(l.response.content_body)
        self.assertEqual(l.response.status_code, 200)
        self.assertIsNotNone(l.response.headers)
        self.assertIsNotNone(l.response.response_on)
        #
        self.assertEqual(LogHttpRequest.objects.count(), 1)
