import uuid
from datetime import datetime
import time
import simplejson as json
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model

from .custom_types import Amount, Transaction
from ...common.abstract.models import AbstractBaseModel
from ...common.currencies import DEFAULT_CURRENCY


class Account(AbstractBaseModel):
    """
    Account
    """
    __table_name__ = 'account'

    owner_id = columns.UUID(primary_key=True)
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    name = columns.Text()
    type = columns.Text(discriminator_column=True)


class CurrentAccount(Account):
    """
    CurrentAccount
    """
    __discriminator_value__ = 'current'
    available = columns.UserDefinedType(Amount)
    pending = columns.Set(columns.UserDefinedType(Transaction))

    @classmethod
    def create(cls, **kwargs):
        kwargs['available'] = Amount(amount=0, currency=DEFAULT_CURRENCY[0])
        return super(CurrentAccount, cls).create(**kwargs)
