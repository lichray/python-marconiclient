

from misc import proc_template


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

    def read(self):
        """ Gets this message and returns the content, includinig all metadata """
        hdrs, body = self._conn._perform_http(href=self._href, method='GET')

        return body

    def delete(self):
        # Note: marconi currently treats messages as idempotent, so
        # we should never receive a 404 back
        self._conn._perform_http(href=self._href, method='DELETE')
