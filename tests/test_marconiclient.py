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

class TestClientException(testtools.TestCase):

    def test_exception(self):
        # Basic instantiation and inheritance check
        ex = ClientException("Something bad happened")
        self.assertTrue(isinstance(ex, Exception))

   
    #TODO Use dependency injection to mock HTTP(S)Client 
    def test_connection(self):
        """ 
        conn = Connection(authurl="https://identity.api.rackspacecloud.com/v2.0", 
                          endpoint="http://166.78.150.92:8888/v1/1",
                          user="", key="")

        conn.connect()

        self.assertIsNotNone(conn.endpoint)
        self.assertIsNotNone(conn.authurl)

        queue_name = 'this-is-a-demo-queue8'

        conn.create_queue(queue_name, 500)

        metadata = conn.get_queue_metadata(queue_name)

        self.assertEquals(metadata['messages']['ttl'], 502)
        """
