import simplejson as json
from ..utils.json import GeneralEncoder


class JsonMixin(object):
    """
    JsonMixin
    """
    def to_dict(self):
        """ Returns a map of column names to cleaned values """
        values = {}
        # object
        if hasattr(self, 'object'):
            values['object'] = self.object
        # items
        for key, val in self.items():
            values[key] = val
        return values

    def to_json(self):
        return json.dumps(self.to_dict(), cls=GeneralEncoder)
