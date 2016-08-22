import uuid
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model

from .abstract_models import AbstractUser
from .custom_types import (Profile, Address)


class User(AbstractUser):
    """
    Users within the Flask authentication system are represented by this model.
    """
    __table_name__ = 'user'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    profile = columns.UserDefinedType(Profile)
    address = columns.UserDefinedType(Address)
    is_verified = columns.Boolean(default=False)

    @classmethod
    def create(cls, **kwargs):

        password = kwargs.get('password')
        kwargs['password'] = cls.hash_password(password)
        return super(User, cls).create(**kwargs)
