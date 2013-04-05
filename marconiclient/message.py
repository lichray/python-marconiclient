

from misc import http_connect, proc_template, perform_http, require_authenticated
from misc import require_clientid

class NoSuchMessageError(Exception):
    def __init__(self, name):
        pass

class Message(object):

    def __init__(self, conn, url, content=None):
        """
        Creates a message object. This class should never
        be instantiated directly by a user

        :param
        """
        self._conn = conn
        self._url = url

        self._content = content

    def __getitem__(self, key):
        if self._content:
            return self._content[key]
        else:
            raise KeyError()

    @property
    def url(self):
        return self._url

    @property
    def body(self):
        return ''

    @require_authenticated
    @require_clientid
    def read(self, headers, **kwargs):
        """ Gets this message and returns the content, includinig all metadata """
        hdrs, body = perform_http(url=self._url, method='GET', headers=headers)
        return body

    @require_authenticated
    @require_clientid
    def delete(self, headers, **kwargs):
        # Note: marconi currently treats messages as idempotent, so
        # we should never receive a 404 back
        perform_http(url=self._url, method='DELETE', headers=headers)
