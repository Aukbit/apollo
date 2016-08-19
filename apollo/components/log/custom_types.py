import logging
logger = logging.getLogger(__name__)
import simplejson as json
from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from .general import HTTP_METHODS_STRING_MAP
from ...common.utils.json import HttpHeadersEncoder


class Request(UserType):
    """
    Request type
    """
    machine = columns.Text()
    ip = columns.Text()
    content_type = columns.Text()
    content_body = columns.Text()
    url = columns.Text()
    method = columns.Integer()
    headers = columns.Text()
    request_on = columns.DateTime()

    @classmethod
    def validate_request(cls, request):
        try:
            r = cls()
            if hasattr(request, 'user_agent'):
                r.machine = request.user_agent.string
            if hasattr(request, 'remote_addr'):
                r.ip = request.remote_addr
            if hasattr(request, 'content_type'):
                r.content_type = request.content_type
            if hasattr(request, 'data'):
                r.content_body = request.data
            if hasattr(request, 'url'):
                r.url = request.url
            if hasattr(request, 'method'):
                r.method = HTTP_METHODS_STRING_MAP[request.method]
            if hasattr(request, 'headers'):
                r.headers = json.dumps(request.environ, cls=HttpHeadersEncoder)
            r.request_on = datetime.utcnow()
            return r
        except Exception as e:
            logger.error('Log request error: %s' % e)


class Response(UserType):
    """
    Response type
    """
    content_type = columns.Text()
    content_body = columns.Text()
    status_code = columns.SmallInt()
    headers = columns.Text()
    response_on = columns.DateTime()

    @classmethod
    def validate_response(cls, response):
        try:
            r = cls()
            if hasattr(response, 'content_type'):
                r.content_type = response.content_type
            if hasattr(response, 'data'):
                r.content_body = response.data
            if hasattr(response, 'status_code'):
                r.status_code = response.status_code
            if hasattr(response, 'headers'):
                r.headers = json.dumps(response.headers.items(), cls=HttpHeadersEncoder)
            r.response_on = datetime.utcnow()
            return r
        except Exception as e:
            logger.error('Log response error: %s' % e)
