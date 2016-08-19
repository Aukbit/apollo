
import datetime
import base64

from flask import url_for

from cassandra.cqlengine.management import drop_table

from apollo.common.database import init_db, get_db
from apollo.tests.mixins import TestAppEngineMixin
from apollo.components.user.models import User, Profile, Address


class UserTestCase(TestAppEngineMixin):

    def setUp(self):
        super(UserTestCase, self).setUp()
        init_db(models=[User], types=[Profile, Address])
        self.db = get_db()

    def tearDown(self):
        super(UserTestCase, self).tearDown()
        drop_table(User)

    def test_create_user(self):
        self.assertEqual(User.objects.count(), 0)
        p = Profile(first_name='Luke',
                    last_name='Skywalker',
                    dob_date=datetime.date(1981, 6, 28),
                    gender='m',
                    biography='biography')
        a = Address(name='home',
                    line_1='line_1',
                    line_2='line_2',
                    town_city='town_city',
                    county='county',
                    zipcode='123',
                    )
        # create
        u = User.create(username='luke',
                        password='123456',
                        email='luke.skywalker@aukbit.com',
                        profile=p,
                        address=a)
        # assert
        self.assertIsInstance(u, User)
        self.assertIsNotNone(u.id)
        self.assertFalse(u.is_verified)
        # profile
        self.assertEqual(u.profile.first_name, 'Luke')
        self.assertEqual(u.profile.last_name, 'Skywalker')
        self.assertEqual(u.profile.dob_date, datetime.date(1981, 6, 28))
        self.assertEqual(u.profile.gender, 'm')
        self.assertEqual(u.profile.biography, 'biography')
        # address
        self.assertEqual(u.address.name, 'home')
        self.assertEqual(u.address.line_1, 'line_1')
        self.assertEqual(u.address.line_2, 'line_2')
        self.assertEqual(u.address.town_city, 'town_city')
        self.assertEqual(u.address.county, 'county')
        self.assertEqual(u.address.zipcode, '123')
        # AbstractUser
        self.assertEqual(u.username, 'luke')
        self.assertTrue(u.verify_password('123456'))
        self.assertEqual(u.email, 'luke.skywalker@aukbit.com')
        self.assertFalse(u.is_staff)
        # AbstractBaseModel
        self.assertEqual(u.object, 'user')
        self.assertIsNotNone(u.changed_on)
        self.assertIsNotNone(u.created_on)
        self.assertTrue(u.super_active)


