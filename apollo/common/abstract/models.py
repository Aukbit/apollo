import logging
logger = logging.getLogger(__name__)
import simplejson as json
from datetime import datetime

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class AbstractBaseModel(Model):
    """
    AbstractBaseModel
    This model is only intended to be used as a base class for other models
    """
    __abstract__ = True

    changed_on = columns.DateTime()
    created_on = columns.DateTime(default=datetime.utcnow())
    # super_active field, in case admin staff needs to disable the entry
    super_active = columns.Boolean(default=True)

    # --------------
    # Super Methods
    # --------------
    def save(self):
        self.changed_on = datetime.utcnow()
        return super(AbstractBaseModel, self).save()

    def update(self, **values):
        self.changed_on = datetime.utcnow()
        return super(AbstractBaseModel, self).update(**values)

    # --------------
    # Properties
    # --------------
    @property
    def object(self):
        return self.__table_name__
