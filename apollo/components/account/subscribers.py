import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import CurrentAccount
from ...common.subscriber import Subscriber


class UserSubscriber(Subscriber):

    @staticmethod
    def create_current_account(event):
        data = json.loads(event.data)
        account_name = '{} current account'.format(data.get('username'))
        CurrentAccount.create(owner_id=event.parent_id,
                              name=account_name)

    def on_save(self, sender, **kwargs):
        super(UserSubscriber, self).on_save(sender, **kwargs)
        event = kwargs.get('instance', None)
        if event is not None and event.type == 'user.created':
            self.create_current_account(event)


user_subscriber = UserSubscriber(senders=['event.user.created'])
