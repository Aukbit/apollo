import logging
logger = logging.getLogger(__name__)
import os
import simplejson as json
from datetime import datetime
import stripe
from flask import (current_app)
from google.appengine.api import urlfetch
from google.appengine.runtime import DeadlineExceededError

from .general import *


class StripeMixin(object):
    """
    StripeMixin
    """
    @staticmethod
    def _call(f, *args, **kwargs):
        """

        :param f:
        :return:
        """
        try:
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', os.getenv('STRIPE_SECRET_KEY', ''))
            return f(*args, **kwargs)
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            exception = e
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            exception = e
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            exception = e
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            exception = e
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            exception = e
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            exception = e
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            exception = e
        error = {'error': exception.json_body.get('error') if exception.json_body is not None else exception}
        logger.error('error: %s data: %s' % (error, kwargs))
        return error

    @staticmethod
    def get_or_create_customer(*args, **kwargs):
        """
        create_vault always via payment nonce received from client JS, does not matter if its CC or PayPal
        :param parent: User Key
        :param payment_method_nonce:
        :param billing_address:
        :return: stripe customer Json object
        """
        def f(*args, **kwargs):
            customer_id = kwargs.get('customer_id')
            if customer_id is not None:
                customer = stripe.Customer.retrieve(customer_id)
                # set new payment method as default
                customer.source = kwargs.get('payment_method_nonce')
                customer.save()
            else:
                customer = stripe.Customer.create(
                    description='%s' % kwargs.get('username'),
                    metadata=kwargs.get('metadata'),
                    source=kwargs.get('payment_method_nonce')
                )
            return customer
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def create_customer(*args, **kwargs):
        """

        :return:
        """
        def f(*args, **kwargs):
            email = kwargs.get('email')
            customer = stripe.Customer.create(
                    description='Customer for {}'.format(email),
                    email=email,
                    metadata=kwargs.get('metadata'),
                )
            return customer
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def delete_customer(*args, **kwargs):
        """

        :return:
        """
        def f(*args, **kwargs):
            customer = stripe.Customer.retrieve(kwargs.get('customer_id'))
            response = customer.delete()
            return response.deleted is True
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def get_or_create_connect_account(*args, **kwargs):
        """
        create_connect_account_in_vault
        Note this method is currently used only in tests, oauth is the way to go
        :return:
        """
        def f(*args, **kwargs):
            account_id = kwargs.get('account_id')
            if account_id is not None:
                account = stripe.Account.retrieve(account_id)
            else:
                account = stripe.Account.create(
                  managed=kwargs.get('managed'),
                  country=kwargs.get('country'),
                  email=kwargs.get('email')
                )
            return json.loads(json.dumps(account))
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def create_account(*args, **kwargs):
        """

        :return:
        """
        def f(*args, **kwargs):
            email = kwargs.get('email')
            country = kwargs.get('country')
            currency = kwargs.get('currency')
            # legal_entity
            legal_entity = dict()
            legal_entity['first_name'] = kwargs.get('first_name')
            legal_entity['last_name'] = kwargs.get('last_name')
            legal_entity['type'] = 'individual'
            dob_date = kwargs.get('dob_date')
            if isinstance(dob_date, datetime):
                legal_entity['dob']['day'] = dob_date.day
                legal_entity['dob']['month'] = dob_date.month
                legal_entity['dob']['year'] = dob_date.year

            account = stripe.Account.create(
                email=email,
                country=country,
                debit_negative_balances=True,
                decline_charge_on={
                    "avs_failure": False,
                    "cvc_failure": True
                },
                default_currency=currency,
                managed=True,
                legal_entity=legal_entity,
                transfer_schedule={'interval': 'manual'}
            )
            return account
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def delete_account(*args, **kwargs):
        """

        :return:
        """
        def f(*args, **kwargs):
            account = stripe.Account.retrieve(kwargs.get('account_id'))
            response = account.delete()
            return response.deleted is True
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def create_charge(*args, **kwargs):
        """

        :return:
        """
        def f(*args, **kwargs):
            charge = stripe.Charge.create(
                amount=kwargs.get('amount_value'),
                currency=kwargs.get('amount_currency'),
                application_fee=kwargs.get('service_value'),
                customer=kwargs.get('source_id'),
                destination=kwargs.get('destination_id'),
                description=kwargs.get('description'),
                metadata=kwargs.get('metadata')
            )
            return json.loads(json.dumps(charge))
        return StripeMixin._call(f, *args, **kwargs)

    @staticmethod
    def create_refund(*args, **kwargs):
        """
        create_refund

        https://stripe.com/docs/connect/payments-fees#issuing-refunds
        Stripe Notes:
        When refunding a charge that has a destination value, by default the destination account will keep the funds
        that were transferred to it, leaving the platform account to cover the negative balance from the refund.
        To pull back the funds from the connected account to cover the refund,
        set the reverse_transfer parameter to true when creating the refund.
        :return:
        """
        def f(*args, **kwargs):
            refund = stripe.Refund.create(
                charge=kwargs.get('charge_id'),
                reverse_transfer=True,
                reason=kwargs.get('reason'),
                metadata=kwargs.get('metadata')
            )
            return json.loads(json.dumps(refund))
        return StripeMixin._call(f, *args, **kwargs)
