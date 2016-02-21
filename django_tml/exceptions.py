from tml.exceptions import Error

class CookieNotParsed(Error):

    def __init__(self, real_exception):
        self._e = real_exception

    def __str__(self):
        return "Parse cookie error: %s" % self._e.message
