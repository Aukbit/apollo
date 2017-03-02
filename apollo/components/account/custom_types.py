from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from ...common.mixins.json import JsonMixin


class Amount(UserType, JsonMixin):
    """
    Amount
    """
    amount = columns.BigInt(required=True)
    currency = columns.Text(min_length=3, max_length=3, required=True)

    def add(self, value=None):
        if isinstance(value, Amount) and value.currency == self.currency:
            self.amount += value.amount

    def sub(self, value=None):
        if isinstance(value, Amount) and value.currency == self.currency:
            self.amount -= value.amount

    def update(self, operation=None):
        if isinstance(operation, Operation):
            if operation.type == 'debit':
                self.sub(operation.value)
            elif operation.type == 'credit':
                self.add(operation.value)


class Operation(UserType, JsonMixin):
    """
    Operation
    """
    value = columns.UserDefinedType(Amount, required=True)
    type = columns.Text(required=True)


class Transaction(UserType, JsonMixin):
    """
    Transaction
    """
    value = columns.UserDefinedType(Amount, required=True)
    type = columns.Text(required=True)
    event_id = columns.UUID(required=True)
