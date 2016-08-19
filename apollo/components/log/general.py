# **************
# Http methods
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
# **************

OPTIONS = 1, 'OPTIONS'
GET = 2, 'GET'
HEAD = 3, 'HEAD'
POST = 4, 'POST'
PUT = 5, 'PUT'
DELETE = 6, 'DELETE'
TRACE = 7, 'TRACE'
CONNECT = 8, 'CONNECT'


HTTP_METHODS_STRING_MAP = {
    OPTIONS[1]: OPTIONS[0],
    GET[1]: GET[0],
    HEAD[1]: HEAD[0],
    POST[1]: POST[0],
    PUT[1]: PUT[0],
    DELETE[1]: DELETE[0],
    TRACE[1]: TRACE[0],
    CONNECT[1]: CONNECT[0]
}

HTTP_METHODS_CHOICES = frozenset(HTTP_METHODS_STRING_MAP.values())
HTTP_METHODS_STRING_CHOICES = frozenset(HTTP_METHODS_STRING_MAP.keys())
HTTP_METHODS_MAP = dict(zip(HTTP_METHODS_STRING_MAP.values(), HTTP_METHODS_STRING_MAP.keys()))

CRUD_METHODS = ('POST', 'GET', 'PUT', 'DELETE')
