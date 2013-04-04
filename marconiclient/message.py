

from misc import http_connect, proc_template, perform_http, require_authenticated
from misc import require_clientid

class NoSuchMessageError(Exception):
    def __init__(self, name):
        pass

class Message(object):

    def __init__(self, conn, url):
        """
        Creates a message object. This class should never
        be instantiated directly by a user

        :param
        """
        self._conn = conn
        self._url = url

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

    def delete(self, headers, **kwargs):
        try:
            hdrs, body = perform_http(url=self._url, method='DELETE', headers=headers)
        except ClientException as ex:
            raise NoSuchMessageError(queue_name) if ex.http_status == 404 else ex
