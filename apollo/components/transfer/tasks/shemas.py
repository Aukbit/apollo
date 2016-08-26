
from marshmallow import (Schema, fields, validate, validates, validates_schema,
                         pre_dump, post_dump, pre_load, post_load, ValidationError)


class ActionSchema(Schema):
    """
    ActionSchema
    """
    action = fields.Str(validate=[validate.Length(min=4, max=32)],
                        required=True)
    metadata = fields.Dict()

    @validates('action')
    def validate_action(self, data):
        if not data:
            raise ValidationError('Action not provided.')

        instance = self.context.get('instance')
        if not instance.is_action_valid(data):
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
