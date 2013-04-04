
class ClientException(Exception):
    """Exception for wrapping up Marconi client errors"""
    def __init__(self, url='', http_status=0,
                 method='', http_response_content=''):

        self.method = method
        self.url = url
        self.http_status = http_status
        self.http_response_content = http_response_content

        msg = "%s %s returned %d" % (self.method, self.url, self.http_status)
        Exception.__init__(self, msg)

