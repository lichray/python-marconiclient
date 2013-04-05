
class Claim(object):

    def __init__(self, conn, url, messages):
        """
        :param: conn The conn to use for manipulating this claim
        :param: url The fully-qualified URL for this claim
        :param: messages A list of messages belonging to this claim
        """
        self._conn = conn
        self._url = url
        self._msgs = messages


    def messages(self):
        """
        Returns the messages associated with this claim
        """
        return self._msgs


    @require_authenticated
    @require_clientid
    def update(self, ttl, headers, **kwargs)
        """
        Updates this claim with the specified ttl
        """
        body = {"ttl":ttl}
        perform_http(url=self._url, method='PATCH', body=body, headers=headers)


    @require_authenticated
    @require_clientid
    def release(self, headers, **kwargs):
        """
        Releases the current claim
        """
        perform_http(self._url, method='DELETE', headers=headers)
