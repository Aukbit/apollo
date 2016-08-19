import simplejson as json
import datetime
from google.appengine.ext import ndb
# use as
# print json.dumps(obj, cls = MyEncoder)


class GeneralEncoder(json.JSONEncoder):
    """
    MyEncoder
    to be used as json.dumps(obj, cls = MyJsonEncoder)
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, ndb.Key):
            return obj.urlsafe()
        return json.JSONEncoder.default(self, obj)


class HttpHeadersEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj.__class__ in [str, int, float, bool, list, dict]:
            return json.JSONEncoder.default(self, obj)
        return None
