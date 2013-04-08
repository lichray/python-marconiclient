

from misc import proc_template, require_authenticated
from misc import require_clientid


class NoSuchMessageError(Exception):
    def __init__(self, name):
        pass


class Message(object):

    def __init__(self, conn, href, content=None):
        """
        Creates a message object. This class should never
        be instantiated directly by a user

        :param
        """
        self._conn = conn
        self._href = href
        self._content = content

    def __getitem__(self, key):
        if self._content:
            return self._content[key]
        else:
            raise KeyError()

    @property
    def href(self):
        return self._href

    @require_authenticated
    @require_clientid
    def read(self, headers, **kwargs):
        """ Gets this message and returns the content, includinig all metadata """
        hdrs, body = self._conn._perform_http(
            href=self._href, method='GET', headers=headers)
        return body

    @require_authenticated
    @require_clientid
    def delete(self, headers, **kwargs):
        # Note: marconi currently treats messages as idempotent, so
        # we should never receive a 404 back
        self._conn._perform_http(
            href=self._href, method='DELETE', headers=headers)
