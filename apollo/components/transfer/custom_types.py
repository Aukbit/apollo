from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from ..account.custom_types import Amount
from ...common.mixins.json import JsonMixin


class Task(UserType, JsonMixin):
    """
    Task
    """
    task = columns.Map(columns.Text, columns.Text)

class Worker(UserType, JsonMixin):
    """
    Worker
    """
    tasks = columns.Map(columns.Text, columns.Text)

    def add_task(self, obj=None):
        self.tasks.update(obj)
