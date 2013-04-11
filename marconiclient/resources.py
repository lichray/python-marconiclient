
from misc import proc_template


class Queue(object):

    def __init__(self, conn, name, href, metadata=None):
        """
        Creates a new queue object. This class should
        never be instantiated directly but should be
        used with Connection.create_queue or
        Connection.get_queue
        """
        self._conn = conn
        self._href = href
        self._name = name
        self._metadata = metadata

        self._get_messages_href = None

        self._messages_template = href + "/messages"
        self._message_template = href + "/messages/{message_id}"
        self._claims_template = href + "/claims?limit={limit}"
        self._claim_template = href + "/claims/{claim_id}"

    @property
    def metadata(self):
        return self._metadata

    def update_metadata(self, metadata):
        self._conn._perform_http(href=self._href,
                                 method='PUT',
                                 request_body=metadata)

        self._metadata = metadata

    @property
    def href(self):
        return self._href

    def post_message(self, message, ttl):
        """
        Posts a single message with the specified ttl
        :param ttl: The TTL to set on this message
        """
        href = proc_template(self._conn.messages_href, queue_name=self.name)

        body = [{"ttl": ttl, "body": message}]

        hdrs, body = self._conn._perform_http(
            href=href, method='POST', request_body=body)

        location = hdrs['location']

        return Message(conn=self._conn, href=location)

    def claim(self, ttl, grace, limit=5):
        """
        Claims a set of messages. The server configuration determines
        the maximum number of messages that can be claimed.
        """
        href = proc_template(self._claims_template, limit=str(limit))

        body = {"ttl": ttl, "grace": grace}

        hdrs, body = self._conn._perform_http(
            href=href, method='POST', request_body=body)

        # Build a list of Message objects using a list comprehesion
        msgs = [Message(self._conn, href=msg[
                        'href'], content=msg) for msg in body]

        location = hdrs['location']

        return Claim(conn=self._conn, messages=msgs, href=location)

    def get_message(self, message_id):

        href = proc_template(self._conn.message_href, message_id)

    def get_messages(self, echo=False, restart=False):
        """
        TODO(jdp): Comment me
        """
        if not self._get_messages_href or restart:
            self._get_messages_href = proc_template(self._conn.messages_href,
                                                    queue_name=self.name)

            if echo:
                self._get_messages_href += "?echo=true"

        truncated = True  # Was the current request truncated?

        while truncated:
            truncated = False

            hdrs, body = self._conn._perform_http(
                href=self._get_messages_href, method='GET')

            if not body:
                # Empty body, just short-circuit and return
                return

            for link in body['links']:
                if link['rel'] == 'next':
                    self._get_messages_href = link['href']
                    truncated = True

            for message in body['messages']:
                yield Message(self._conn,
                              href=message['href'],
                              content=message)

    def get_stats(self):
        """Retrieves statistics about the queue"""
        href = proc_template(self._conn.stats_href, queue_name=self._name)

        hdrs, body = self._conn._perform_http(href=href, method='GET')

        return body

    @property
    def name(self):
        """The name of this queue"""
        return self._name


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
        """
        Gets this message and returns the content, includinig all metadata
        """
        hdrs, body = self._conn._perform_http(href=self._href, method='GET')

        return body

    def delete(self):
        # Note: marconi currently treats messages as idempotent, so
        # we should never receive a 404 back
        self._conn._perform_http(href=self._href, method='DELETE')


class Claim(object):

    def __init__(self, conn, href, messages):
        """
        :param: conn The conn to use for manipulating this claim
        :param: href The fully-qualified URL for this claim
        :param: messages A list of messages belonging to this claim
        """
        self._conn = conn
        self._href = href
        self._msgs = messages

    @property
    def messages(self):
        """
        Returns the messages that were associated with
        this claim at creation time.
        """
        return self._msgs

    def read(self):
        """
        Gets the claim metadata and the associated messages.
        """
        hdrs, body = self._conn._perform_http(href=self._href, method='GET')

        return body

    def update(self, ttl):
        """
        Updates this claim with the specified TTL
        """
        body = {"ttl": ttl}
        self._conn._perform_http(href=self._href, method='PATCH', body=body)

    def release(self):
        """
        Releases the current claim
        """
        self._conn._perform_http(href=self._href, method='DELETE')
