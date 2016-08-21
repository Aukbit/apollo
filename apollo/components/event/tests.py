
import datetime
import base64

from mock import MagicMock, Mock, patch
from flask import request, g, url_for
from cassandra.cqlengine.management import drop_table
from apollo.common.database import init_db, get_db
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.user.models import User, Profile
from apollo.components.user.decorators import deco_auth_user
from apollo.components.event.models import Event, EventApi, EventBot
from apollo.components.event.general import ACTIONS_MAP, CREATED, UPDATED


class EventTestCase(TestAppEngineMixin):

    def setUp(self):
        super(EventTestCase, self).setUp()
        init_db(models=[EventApi, EventBot, User])
        self.db = get_db()

    def tearDown(self):
        super(EventTestCase, self).tearDown()
        drop_table(EventApi)
        drop_table(EventBot)
        drop_table(User)

    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    def test_create_event(self):
        # get events
        events = Event.objects.all()
        self.assertEqual(len(events), 1)
        self.assertIsNotNone(events[0].id)
        self.assertEqual(events[0].parent_id, self.luke.id)
        self.assertEqual(events[0].action, CREATED[0])
        self.assertEqual(events[0].data, self.luke.to_json())

    @deco_auth_user(username="luke", email="test.luke.skywalker@aukbit.com", password="123456")
    def test_update_event(self):
        # assert events
        self.assertEqual(Event.objects.count(), 1)
        # update user
        self.luke.profile = Profile(first_name='luke', last_name='skywalker')
        self.luke.save()
        # assert
        self.assertEqual(Event.objects.count(), 2)
        events = Event.objects.filter(parent_id=self.luke.id).order_by('id')
        self.assertEqual(events[1].action, UPDATED[0])

