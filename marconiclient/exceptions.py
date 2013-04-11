
class ClientException(Exception):
    """Exception for wrapping up Marconi client errors"""
    def __init__(self, href='', http_status=0,
                 method='', http_response_content=''):

        self.method = method
        self.href = href
        self.http_status = http_status
        self.http_response_content = http_response_content

        msg = "%s %s returned %d" % (self.method, self.href, self.http_status)
        Exception.__init__(self, msg)


class NoSuchQueueError(Exception):
    def __init__(self, name):
        self._queue_name = name

    def __str__(self):
        return "Queue '%s' not found" % (self._queue_name)


class NoSuchMessageError(Exception):
    def __init__(self, name):
        pass
