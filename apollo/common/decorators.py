
from functools import wraps
from flask import make_response, jsonify


def get_object(model=None):
    """
    get_object easily assign self.object with an model instance
    :param model:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            id = kwargs.get('id', None)
            if id is not None and model is not None:
                object = model.objects(id=id).get()
                setattr(args[0], 'object', object)
            return func(*args, **kwargs)
        return func_wrapper
    return decorator


def only_owner_has_object_permission(f):
    """
    only_owner_has_object_permission to only allow owners of an object to edit it.
    :param f:
    :return:
    """
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        object = getattr(args[0], 'object', None)
        user = kwargs.get('user')
        if object is None or user is None or (object.owner_key != user.key and not user.is_automatic):
            return make_response(jsonify({}), 403)
        return f(*args, **kwargs)
    return func_wrapper


def only_buyer_or_seller_has_object_permission(f):
    """
    only_buyer_or_seller_has_object_permission to only allow owners of an object to edit it.
    :param f:
    :return:
    """
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        object = getattr(args[0], 'object', None)
        user = kwargs.get('user')
        if object is None or user is None or (object.seller_key != user.key and object.buyer_key != user.key and not user.is_automatic):
            return make_response(jsonify({}), 403)
        return f(*args, **kwargs)
    return func_wrapper


def only_status_has_object_permission(status=[]):
    """
    only_status_has_object_permission to only allow changes while in status list.
    :param model:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            object = getattr(args[0], 'object', None)
            if object is None or object.status not in status:
                return make_response(jsonify({}), 403)
            return func(*args, **kwargs)
        return func_wrapper
    return decorator


def only_parent_status_has_object_permission(status=[]):
    """
    only_status_has_object_permission to only allow changes while in status list.
    :param model:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            object = getattr(args[0], 'object', None)
            parent = object.parent_key.get()
            if object is None or parent is None or parent.status not in status:
                return make_response(jsonify({}), 403)
            return func(*args, **kwargs)
        return func_wrapper
    return decorator