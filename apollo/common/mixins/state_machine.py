import logging
import inspect
logger = logging.getLogger(__name__)

from transitions import Machine, MachineError


class MachineMixin(object):
    """
    MachineMixin
    """
    @staticmethod
    def _trigger(action):
        return 'go_{}'.format(action)

    def is_action_valid(self, action):
        trigger = self._trigger(action)
        return hasattr(self, 'machine') and \
               isinstance(self.machine, Machine) and \
               trigger in self.machine.events

    def run_action(self, action, **kwargs):
        if self.is_action_valid(action):
            try:
                trigger = self._trigger(action)
                run = getattr(self, trigger)
                return run(**kwargs)
            except MachineError as e:
                logger.error('%s error: %s' % (self._class_name(), e))
        return False
