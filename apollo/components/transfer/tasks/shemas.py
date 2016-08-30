import simplejson as json
from marshmallow import (Schema, fields, validate, validates, validates_schema,
                         pre_dump, post_dump, pre_load, post_load, ValidationError,
                         utils)
from marshmallow.fields import Field


class Json(Field):
    """A json field. Supports dicts and dict-like objects.

    .. note::
        This field is only appropriate when the structure of
        nested data is not known. For structured data, use
        `Nested`.

    .. versionadded:: 2.1.0
    """

    default_error_messages = {
        'invalid': 'Not a valid json type.'
    }

    def __init__(self, *args, **kwargs):
        return super(Json, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return json.dumps(value)

    def _deserialize(self, value, attr, data):
        if isinstance(value, basestring):
            return json.loads(value)
        else:
            self.fail('invalid')


class ActionSchema(Schema):
    """
    ActionSchema
    """
    action = fields.Str(validate=[validate.Length(min=4, max=32)],
                        required=True)
    metadata = Json()

    @validates('action')
    def validate_action(self, data):
        if not data:
            raise ValidationError('Action not provided.')

        instance = self.context.get('instance')
        if instance is not None and not instance.is_action_valid(data):
            raise ValidationError('Action invalid: %s' % data)

    # @post_load
    # def add_action_user_to_metadata(self, data):
    #     # print 'post_load {}'.format(data)
    #     action = data.get('action')
    #     metadata = data.get('metadata', {})
    #     user = self.context.get('user')
    #     action_user = '{}_user'.format(action)
    #     metadata.update({action_user: user.username})
    #     data['metadata'] = metadata
    #     return data
