# Copyright (c) 2010-2012 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import testtools
from marconiclient import *
from eventlet import GreenPool
import uuid
from urlparse import urlparse



class TestClientException(testtools.TestCase):

    def test_exception(self):
        # Basic instantiation and inheritance check

        ex = ClientException("Something bad happened")
        self.assertTrue(isinstance(ex, Exception))


    #TODO Use dependency injection to mock HTTP(S)Client
    def test_connection(self):

        """
        conn = Connection(auth_endpoint="https://identity.api.rackspacecloud.com/v2.0",
                          client_id=str(uuid.uuid4()),
                          endpoint="http://localhost:8888/v1/12345",
                          user="", key="")

        """

        conn = Connection(auth_endpoint="https://identity.api.rackspacecloud.com/v2.0",
                          client_id=str(uuid.uuid4()),
                          endpoint="http://166.78.143.130/v1/12345",
                          user="", key="")


        conn.connect(token='blah')

        def create_worker(queue_name):
            return conn.create_queue(queue_name, 100)

        def post_worker(queue):
            return queue.post_message('test_message', 10)

        def delete_worker(queue_name):
            conn.delete_queue(queue_name)
            return queue_name

        pool = GreenPool(100)


        def on_message_posted(greenthread):
            msg = greenthread.wait()
            print msg._href

        def on_queue_created(greenthread):
            queue = greenthread.wait()
            print queue.name

            """

            for x in range(0, 1000):
                gt = pool.spawn(post_worker, queue)
                gt.link(on_message_posted)
            """

        queue_names = ["queue-"+str(x) for x in xrange(0,50000)]

        for queue_name in queue_names:
            gt = pool.spawn(create_worker, queue_name)
            gt.link(on_queue_created)

        pool.waitall()

        """

        # Now delete the queue
        print "Deleting..."
        for queue_name in queue_names:
            gt = pool.spawn_n(delete_worker, queue_name)

        pool.waitall()
        """

        """"
        queue = conn.create_queue('test_queue', ttl=1000)
        queue = conn.get_queue('test_queue')
        queue = conn.create_queue('test_queue2', ttl=1000)
        queue = conn.create_queue('test_queue3', ttl=1000)


        metadata = queue.metadata
        metadata["messages"]["ttl"] = 321

        queue.update_metadata(metadata)

        print "Creating messages"

        for x in range(0, 10):
            msg = queue.post_message("yyy:"+str(x), 500000)

        print "Done creating messages"

        claim = queue.claim(ttl=10, grace=100, limit=2)

        for msg in claim.messages:
            print "Claimed:", msg._href

        claim.release()

        print "Listing messages..."

        for msg in queue.get_messages(echo=False):
            print "Body:", msg['body'], msg['ttl'], msg['href']

        print "Done listing messages"

        for queue in conn.get_queues():
            print queue.name
            """

        """
        queue = conn.create_queue('test_queue_whatever', 50)
        msg_body = {"username":"buford", "age":32}
        msg = queue.post_message(msg_body, 10000)

        msg.delete()
        """

        # msg = msg.read()

        """
        for queue in pool.imap(create_worker, queue_names):
            print "Created: ", queue.name
        """

        """
        for queue_name in pool.imap(delete_worker, queue_names):
            print "Deleted: ", queue_name
        """
