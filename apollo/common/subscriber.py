import sys
import logging
logger = logging.getLogger(__name__)

from blinker import signal, ANY

# **************
# GENERAL Signals
# **************
on_save = signal('on_save')
on_event = signal('on_event')


class Subscriber(object):

    def __init__(self, senders=None):
        def handle_on_save(*args, **kwargs):
            self.on_save(*args, **kwargs)
        self.handle_on_save = handle_on_save

        def handle_on_event(*args, **kwargs):
            self.on_event(*args, **kwargs)
        self.handle_on_event = handle_on_event

        # connect
        if senders is not None:
            for sender in senders:
                on_save.connect(handle_on_save, sender=sender)
                on_event.connect(handle_on_event, sender=sender)
        else:
            on_save.connect(handle_on_save, sender=ANY)
            on_event.connect(handle_on_event, sender=ANY)

    @staticmethod
    def info(signal, sender, **kwargs):
        if kwargs.get('logging'):
            instance = kwargs.get('instance', None)
            logger.info('Caught signal: %s from %s : %s' % (signal, sender, instance))

    def on_save(self, sender, **kwargs):
        func_name = sys._getframe().f_code.co_name
        self.info(func_name, sender, **kwargs)
        pass

    def on_event(self, sender, **kwargs):
        func_name = sys._getframe().f_code.co_name
        self.info(func_name, sender, **kwargs)
        pass

