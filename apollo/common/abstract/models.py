import logging
logger = logging.getLogger(__name__)
import simplejson as json

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class BaseModel(Model):
    """
    BaseModel
    This model is only intended to be used as a base class for other models
    """
    changed_on = columns.DateTime()
    created_on = columns.DateTime()
    # super_active field, in case admin staff needs to disable the entry
    super_active = columns.Boolean(default=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)

    # --------------
    # Properties
    # --------------
    @property
    def object(self):
        return self.__table_name__
