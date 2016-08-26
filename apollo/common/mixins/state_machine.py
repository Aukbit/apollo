import logging
import inspect
logger = logging.getLogger(__name__)

from transitions import Machine, MachineError


class MachineMixin(object):
    """
    MachineMixin
    """
    def is_action_valid(self, action):
        return hasattr(self, 'machine') and \
               isinstance(self.machine, Machine) and \
               action in self.machine.events

    def run_action(self, action, **kwargs):
        if self.is_action_valid(action):
            try:
                run = getattr(self, action)
                return run(**kwargs)
            except MachineError as e:
                logger.error('%s error: %s' % (self._class_name(), e))
        return False
