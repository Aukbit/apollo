
class Response(object):
    """
    Response
    """

    def __init__(self, error=None):
        if error is None:
            self.is_success = True
        else:
            self.is_success = False
            self.error = error

    @property
    def error_code(self):
        if isinstance(self.error, tuple):
            return self.error[0]

    @property
    def error_description(self):
        if isinstance(self.error, tuple):
            return self.error[1]
