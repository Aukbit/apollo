
import datetime
import base64

from mock import MagicMock, Mock, patch
from flask import request, g, url_for
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.user.models import User, Profile
from apollo.components.user.decorators import deco_auth_user
from apollo.components.event.models import Event, EventApi, EventBot
from apollo.components.event.general import ACTIONS_MAP, CREATED, UPDATED
from apollo.components.account.subscribers import UserSubscriber as AUS
from apollo.components.payment.subscribers import UserSubscriber as PUS


class EventTestCase(TestAppEngineMixin):

    def setUp(self):
        super(EventTestCase, self).setUp()

    def tearDown(self):
        super(EventTestCase, self).tearDown()

    @patch.object(AUS, 'on_event')
    @patch.object(PUS, 'on_event')
    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    def test_create_event(self, *args):
        # get events
        events = Event.objects.filter(parent_id=self.luke.id).all()
        self.assertEqual(len(events), 1)
        self.assertIsNotNone(events[0].id)
        self.assertEqual(events[0].parent_id, self.luke.id)
        self.assertEqual(events[0].type, 'user.created')
        self.assertEqual(events[0].action, CREATED[0])
        self.assertEqual(events[0].data, self.luke.to_json())

    @patch.object(AUS, 'on_event')
    @patch.object(PUS, 'on_event')
    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    def test_update_event(self, *args):
        # assert events
        events = Event.objects.filter(parent_id=self.luke.id).all()
        # update user
        self.luke.profile = Profile(first_name='luke', last_name='skywalker')
        self.luke.save()
        # assert
        self.assertEqual(Event.objects.filter(parent_id=self.luke.id).count(), 2)
        events = Event.objects.filter(parent_id=self.luke.id).order_by('id')
        self.assertEqual(events[1].type, 'user.updated')
        self.assertEqual(events[1].action, UPDATED[0])

