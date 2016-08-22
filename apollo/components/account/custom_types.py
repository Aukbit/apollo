from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from ...common.mixins.json import JsonMixin


class Amount(UserType, JsonMixin):
    """
    Amount
    """
    amount = columns.BigInt()
    currency = columns.TinyInt()


class Transaction(UserType, JsonMixin):
    """
    Transaction
    """
    value = columns.UserDefinedType(Amount)
    event_id = columns.UUID()
