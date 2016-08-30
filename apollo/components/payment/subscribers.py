import logging
logger = logging.getLogger(__name__)
import simplejson as json

from .models import (PaymentProcessor,
                     StripePaymentProcessor)
from ...common.subscriber import Subscriber


class UserSubscriber(Subscriber):

    @staticmethod
    def create_stripe_payment_processor(user):
        StripePaymentProcessor.create(owner_id=user.id, email=user.email)

    def on_event(self, sender, **kwargs):
        super(UserSubscriber, self).on_event(sender, **kwargs)
        event = kwargs.get('instance', None)
        user = kwargs.get('parent', None)
        if event is not None and user is not None:
            self.create_stripe_payment_processor(user)

user_subscriber = UserSubscriber(senders=['event.user.created'])
