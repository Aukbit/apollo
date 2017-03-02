import uuid
from cassandra.cqlengine import columns, ValidationError
from cassandra.cqlengine.models import Model
from .custom_types import Request, Response
from .general import CRUD_METHODS


class Log(Model):
    """
    Log
    """
    __table_name__ = 'log'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    type = columns.Text(discriminator_column=True)


class LogHttpRequest(Log):
    """
    Log requests
    """
    __discriminator_value__ = 'http_request'

    request = columns.UserDefinedType(Request)
    response = columns.UserDefinedType(Response)

    def __init__(self, **values):
        super(LogHttpRequest, self).__init__(**values)
        self.type = self.__discriminator_value__

    @classmethod
    def create(cls, **kwargs):
        from flask import request
        if request:
            kwargs['request'] = Request.validate_request(request)
        return super(LogHttpRequest, cls).create(**kwargs)


def log_http_request():
    from flask import g, request
    if request.method in CRUD_METHODS:
        log = LogHttpRequest.create()
        g._log = log


def log_http_response(response=None):
    if response:
        from flask import g
        if isinstance(getattr(g, '_log', None), LogHttpRequest):
            log = g._log
            log.response = Response.validate_response(response)
            log.save()
