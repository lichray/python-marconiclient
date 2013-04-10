from misc import proc_template, require_authenticated

from message import Message
from claim import Claim
from stats import Stats


class NoSuchQueueError(Exception):
    def __init__(self, name):
        pass


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

    @require_authenticated
    def update_metadata(self, metadata, headers):
        self._conn._perform_http(href=self._href,
                                 method='PUT',
                                 request_body=metadata,
                                 headers=headers)

        self._metadata = metadata

    @property
    def href(self):
        return self._href

    @require_authenticated
    def post_message(self, message, ttl, headers, **kwargs):
        """
        Posts a single message with the specified ttl
        :param ttl: The TTL to set on this message
        """
        href = proc_template(self._conn.messages_href, queue_name=self.name)

        body = [{"ttl": ttl, "body": message}]

        hdrs, body = self._conn._perform_http(
            href=href, method='POST', request_body=body, headers=headers)

        location = hdrs['location']

        return Message(conn=self._conn, href=location)

    @require_authenticated
    def claim(self, headers, ttl, grace, limit=5):
        """
        Claims a set of messages. The server configuration determines
        the maximum number of messages that can be claimed.
        """
        href = proc_template(self._claims_template, limit=limit)

        body = {"ttl": ttl, "grace": grace}
        hdrs, body = self._conn._perform_http(
            href=href, method='POST', request_body=body, headers=headers)

        msgs = [Message(self._conn, href=msg[
                        'href'], content=msg) for msg in body]

        location = hdrs['location']
        return Claim(conn=self._conn, messages=msgs, href=location)

    @require_authenticated
    def get_messages(self, headers, echo=False, restart=False):
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
                href=self._get_messages_href, method='GET', headers=headers)

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

    @require_authenticated
    def get_stats(self, headers):
        """Retrieves statistics about the queue"""
        href = proc_template(self._conn.stats_href, queue_name=self._name)

        hdrs, body = self._conn._perform_http(href=href,
                                              method='GET',
                                              headers=headers)

        return Stats(body)

    @property
    def name(self):
        """The name of this queue"""
        return self._name
