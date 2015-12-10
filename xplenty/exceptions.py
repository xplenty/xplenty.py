import json


class XplentyAPIException(Exception):
    """
    An exception that is raised whenever an error occurred.
    """
    def __init__(self, http_error):
        self.http_error = http_error
        try:
            self.content = json.loads(http_error.read())
            msg = self.content["message"]
        except (ValueError, TypeError, LookupError):
            msg = str(http_error)

        super(XplentyAPIException, self).__init__(msg)
