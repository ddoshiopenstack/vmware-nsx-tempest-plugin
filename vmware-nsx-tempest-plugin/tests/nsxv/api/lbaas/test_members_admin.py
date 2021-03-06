# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_log import log as logging

from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions as ex

from vmware_nsx_tempest.tests.nsxv.api.lbaas import base

CONF = config.CONF

LOG = logging.getLogger(__name__)


class MemberTest(base.BaseAdminTestCase):
    """Test the member creation operation in admin scope in Neutron-LBaaS API

    using the REST client for members:

    """

    @classmethod
    def resource_setup(cls):
        super(MemberTest, cls).resource_setup()
        # core network setup is moved to base class
        cls.load_balancer = cls._create_active_load_balancer(
            tenant_id=cls.tenant_id,
            vip_subnet_id=cls.subnet.get('id'))
        cls.load_balancer_id = cls.load_balancer.get("id")
        cls._wait_for_load_balancer_status(cls.load_balancer_id)
        cls.listener = cls._create_listener(
            loadbalancer_id=cls.load_balancer.get('id'),
            protocol='HTTP', protocol_port=80)
        cls.listener_id = cls.listener.get('id')
        cls.pool = cls._create_pool(protocol='HTTP',
                                    tenant_id=cls.tenant_id,
                                    lb_algorithm='ROUND_ROBIN',
                                    listener_id=cls.listener_id)
        cls.pool_id = cls.pool.get('id')

    @classmethod
    def resource_cleanup(cls):
        super(MemberTest, cls).resource_cleanup()

    @decorators.attr(type='smoke')
    @decorators.idempotent_id('03eeec24-78d8-4c2f-8d6c-4a78817f352e')
    def test_create_member_invalid_tenant_id(self):
        """Test create member with invalid tenant_id"""
        member_opts = {}
        member_opts['address'] = "127.0.0.1"
        # avoid port=80 to avoid duplicate port during failed testings
        member_opts['protocol_port'] = 84
        member_opts['subnet_id'] = self.subnet_id
        member_opts['tenant_id'] = "$232!$pw"
        member = self._create_member(self.pool_id, **member_opts)
        self.addCleanup(self._delete_member, self.pool_id, member['id'])
        self.assertEqual(member['subnet_id'], self.subnet_id)
        self.assertEqual(member['tenant_id'], "$232!$pw")

    @decorators.attr(type='negative')
    @decorators.idempotent_id('01c9ea0c-bdfe-4108-95d1-69ecdc0a1f26')
    def test_create_member_empty_tenant_id(self):
        """Test create member with an empty tenant_id should fail

        Kilo: @decorators.skip_because(bug="1638148")
        """
        member_opts = {}
        member_opts['address'] = "127.0.0.1"
        member_opts['protocol_port'] = 80
        member_opts['subnet_id'] = self.subnet_id
        member_opts['tenant_id'] = ""
        self.assertRaises(ex.BadRequest, self._create_member,
                          self.pool_id, **member_opts)
