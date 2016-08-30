from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from ..account.custom_types import Amount
from ...common.mixins.json import JsonMixin


class CancellationByUser(UserType, JsonMixin):
    """
    CancellationByUser
    """
    id = columns.UUID()


class CancellationByTask(UserType, JsonMixin):
    """
    CancellationByTask
    """
    name = columns.Text()
    queue_name = columns.Text()


class Cancellation(UserType, JsonMixin):
    """
    Cancellation
    """
    __type_name__ = 'cancellation'

    reason = columns.Text()
    user = columns.UserDefinedType(CancellationByUser)
    task = columns.UserDefinedType(CancellationByTask)
    cancelled_on = columns.DateTime()

    def __init__(self, *args, **kwargs):
        super(Cancellation, self).__init__(*args, **kwargs)
        if self.cancelled_on is None:
            self.cancelled_on = datetime.utcnow()

    @property
    def type(self):
        cancelled_by = 'user' if isinstance(self.user, CancellationByUser) else 'task'
        return '{}_by_{}'.format(self.__type_name__, cancelled_by)


class Worker(UserType, JsonMixin):
    """
    Worker
    """
    tasks = columns.Map(columns.Text, columns.Text)

    def add_task(self, obj=None):
        self.tasks.update(obj)
