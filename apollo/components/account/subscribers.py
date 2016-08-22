import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import CurrentAccount
from ...common.subscriber import Subscriber


class UserSubscriber(Subscriber):

    @staticmethod
    def create_current_account(user):
        account_name = '{} current account'.format(user.username)
        CurrentAccount.create(owner_id=user.id,
                              name=account_name)

    def on_event(self, sender, **kwargs):
        super(UserSubscriber, self).on_save(sender, **kwargs)
        event = kwargs.get('instance', None)
        user = kwargs.get('parent', None)
        if event is not None and event.type == 'user.created' and user is not None:
            self.create_current_account(user)


user_subscriber = UserSubscriber(senders=['event.user.created'])
