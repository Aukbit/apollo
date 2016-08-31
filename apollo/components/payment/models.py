import logging
logger = logging.getLogger(__name__)
import uuid
import hashlib
import logging
from decimal import Decimal


from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from transitions import Machine, State

from .exceptions import EmailNotAvailable
from ...common.abstract.models import AbstractBaseModel
from ...processor.stripe.mixins import StripeMixin


class PaymentProcessor(AbstractBaseModel):
    """PaymentProcessor

    """
    __table_name__ = 'payment_processor'
    owner_id = columns.UUID(primary_key=True)
    id = columns.UUID(primary_key=True, default=uuid.uuid1)
    type = columns.Text(primary_key=True, discriminator_column=True)


class StripePaymentProcessor(PaymentProcessor, StripeMixin):
    """
    StripePaymentProcessor
    """
    __discriminator_value__ = 'stripe'
    ext_customer_id = columns.Text()
    ext_connect_account_id = columns.Text()

    def __init__(self, **values):
        super(StripePaymentProcessor, self).__init__(**values)
        self.type = self.__discriminator_value__

    # --------------
    # Super Methods
    # --------------
    @classmethod
    def create(cls, **kwargs):
        email = kwargs.get('email')
        if email is None:
            raise EmailNotAvailable

        stripe_customer = cls.create_customer(**kwargs)
        kwargs['ext_customer_id'] = stripe_customer.get('id')

        del kwargs['email']
        return super(StripePaymentProcessor, cls).create(**kwargs)

    # --------------
    # Super Methods END
    # --------------
    def remove_ext_customer_id(self):
        context = dict()
        context['customer_id'] = self.ext_customer_id
        self.delete_customer(**context)


class PaymentMethod(AbstractBaseModel):
    """
    PaymentMethod
    """
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    owner_id = columns.UUID(index=True)
    processor_gateway = columns.Text(discriminator_column=True)

    credentials = columns.Map(columns.Text, columns.Text)