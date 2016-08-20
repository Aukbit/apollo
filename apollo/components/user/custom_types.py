from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from ...common.mixins.json import JsonMixin


class Profile(UserType, JsonMixin):
    first_name = columns.Text()
    last_name = columns.Text()
    dob_date = columns.Date()
    gender = columns.Text(max_length=1)
    biography = columns.Text()


class Address(UserType, JsonMixin):
    name = columns.Text()
    line_1 = columns.Text()
    line_2 = columns.Text()
    town_city = columns.Text()
    county = columns.Text()
    zipcode = columns.Text()
