import logging
logger = logging.getLogger(__name__)

from google.appengine.ext import ndb
from google.appengine.api import taskqueue


class TaskNameNotAvailable(Exception):
    pass


class TaskQueueMixin(object):
    """
    TaskQueueMixin
    """

    @staticmethod
    def add_task(queue_name='default', **kwargs):
        """
        Enqueue a task as part of a Datastore transaction
        https://cloud.google.com/appengine/docs/python/ndb/transactions
        https://cloud.google.com/appengine/docs/python/taskqueue/queues
        https://cloud.google.com/appengine/docs/python/taskqueue/push/
        :param url:
        :param params:
        :return:
        """
        try:
            task = taskqueue.add(queue_name=queue_name, **kwargs)
            return task
        except (taskqueue.TombstonedTaskError,
                taskqueue.DuplicateTaskNameError,
                taskqueue.BadTransactionStateError,
                taskqueue.BadTaskStateError,
                taskqueue.TooManyTasksError,
                taskqueue.UnknownQueueError) as e:
            logger.error('Task for queue=%s not created. data: %s error: %s' % (queue_name, kwargs, e))

    @staticmethod
    def remove_task(queue_name='default', name=None, **kwargs):
        """
        Deletes a task fro a specific Queue
        https://cloud.google.com/appengine/docs/python/taskqueue/push/deleting-tasks
        :param url:
        :param params:
        :return:
        """
        if name is None:
            raise TaskNameNotAvailable

        try:
            q = taskqueue.Queue(queue_name)
            q.delete_tasks(taskqueue.Task(name=name))
        except (taskqueue.TombstonedTaskError,
                taskqueue.DuplicateTaskNameError,
                taskqueue.BadTransactionStateError,
                taskqueue.BadTaskStateError,
                taskqueue.TooManyTasksError,
                taskqueue.UnknownQueueError) as e:
            logger.error('Task %s in queue=%s not removed. error: %s' % (name, queue_name, e))