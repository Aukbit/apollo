import simplejson as json
from datetime import datetime, date, time
import uuid
# use as
# print json.dumps(obj, cls = MyEncoder)


class GeneralEncoder(json.JSONEncoder):
    """
    MyEncoder
    to be used as json.dumps(obj, cls = MyJsonEncoder)
    """
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return obj.__str__()
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__table_name__') or hasattr(obj, '__type_name__'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


class HttpHeadersEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return json.JSONEncoder.default(self, obj)
        return None
