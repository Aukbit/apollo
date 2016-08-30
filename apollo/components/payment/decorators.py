import simplejson as json
import base64
from functools import wraps


from .models import PaymentMethod
from .test_fixtures import STRIPE_FAKE_CARD_VISA


def deco_payment(username, format=None, payment_fixture=STRIPE_FAKE_CARD_VISA, name='payment_method'):
    """
    deco_campaign to be used in tests, it will campaign a user and token
    :param username:
    :param email:
    :param password:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if getattr(args[0], 'payment_methods', None) is None:
                setattr(args[0], 'payment_methods', [])
                setattr(args[0], name, '')
            if getattr(args[0], username, None) is None:
                print "@deco_auth_user must exist before this decorator"
                return func(*args, **kwargs)
            if format == 'json':
                print "format json not implemented yet"
                return func(*args, **kwargs)
            user = getattr(args[0], username, None)
            # https://stripe.com/docs/testing
            extras = {'username': username}
            payment_method_nonce = payment_fixture
            customer = PaymentMethod.get_or_create_customer(payment_method_nonce=payment_method_nonce, **extras)
            payment_method = PaymentMethod.create(parent=user.key, credentials=customer)
            args[0].payment_methods.append(payment_method)
            setattr(args[0], name, payment_method)
            return func(*args, **kwargs)
        return func_wrapper
    return decorator
