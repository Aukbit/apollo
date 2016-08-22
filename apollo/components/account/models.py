import uuid
from datetime import datetime
import time
import simplejson as json
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model

from .custom_types import Amount, Transaction
from .general import TRANSACTION_PENDING
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

    @property
    def pending_total(self):
        return sum([p.value.amount for p in self.pending])

    @property
    def net(self):
        total = self.available.amount + self.pending_total
        return Amount(amount=total, currency=self.available.currency)


class AccountTransaction(AbstractBaseModel):
    """
    AccountTransaction
    """
    __table_name__ = 'account_transaction'

    account_id = columns.UUID(primary_key=True)
    id = columns.TimeUUID(primary_key=True, clustering_order='DESC', default=uuid.uuid1)
    description = columns.Text()
    value = columns.UserDefinedType(Amount)
    source_id = columns.UUID()
    type = columns.Text(discriminator_column=True)
    status = columns.TinyInt(default=TRANSACTION_PENDING[0], index=True)


class DebitAccountTransaction(AccountTransaction):
    """
    DebitAccountTransaction
    """
    __discriminator_value__ = 'debit'


class CreditAccountTransaction(AccountTransaction):
    """
    CreditAccountTransaction
    """
    __discriminator_value__ = 'credit'
