from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model

# from .abstract_models import AbstractUser
from .custom_types import (Profile, Address)


class User(Model):
    """
    Users within the Flask authentication system are represented by this model.
    """
    __table_name__ = 'users'

    id = columns.UUID(primary_key=True)
    profile = columns.UserDefinedType(Profile)
    address = columns.UserDefinedType(Address)
    is_verified = columns.Boolean(default=False)

    # def validate(self):
    #     super(User, self).validate()
    #     if self.name == 'jon':
    #         raise ValidationError('no jon\'s allowed')