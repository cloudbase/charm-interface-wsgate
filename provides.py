# Copyright 2020 Cloudbase Solutions SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charms import reactive
import charmhelpers.contrib.network.ip as ch_net_ip


class WSGateProvides(reactive.Endpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingress_address = ch_net_ip.get_relation_ip(self.endpoint_name)

    def relation_ids(self):
        return [x.relation_id for x in self.relations]

    def set_ingress_address(self):
        for relation in self.relations:
            relation.to_publish_raw["ingress-address"] = self.ingress_address
            relation.to_publish_raw["private-address"] = self.ingress_address

    def available(self):
        # Nothing is expected from the client, yet.
        return True

    @reactive.when('endpoint.{endpoint_name}.joined')
    def joined(self):
        reactive.clear_flag(self.expand_name('{endpoint_name}.available'))
        reactive.set_flag(self.expand_name('{endpoint_name}.connected'))
        self.set_ingress_address()

    @reactive.when('endpoint.{endpoint_name}.changed')
    def changed(self):
        if self.available():
            reactive.set_flag(self.expand_name('{endpoint_name}.available'))
        else:
            reactive.clear_flag(self.expand_name('{endpoint_name}.available'))

    def remove(self):
        flags = (
            self.expand_name('{endpoint_name}.connected'),
            self.expand_name('{endpoint_name}.available'),
        )
        for flag in flags:
            reactive.clear_flag(flag)

    @reactive.when('endpoint.{endpoint_name}.departed')
    def departed(self):
        self.remove()

    @reactive.when('endpoint.{endpoint_name}.broken')
    def broken(self):
        self.remove()

    def set_wsgate_info(self, relation_id, relation_data):
        if type(relation_data) is not dict:
            # TODO(gsamfira): Should we log? Should we raise?
            relation_data = {}
        url = relation_data.get("html5_proxy_base_url", None)
        if not url:
            return
        self.relations[relation_id].to_publish["html5_proxy_base_url"] = url
        self.relations[relation_id].to_publish["enabled"] = relation_data.get(
            "enabled", False)
        allow_user = relation_data.get("allow_user", None)
        if allow_user:
            # Active directory user. Remote node may need to add this user
            # to specific groups in order to allow RDP connections to VMs.
            self.relations[relation_id].to_publish["allow_user"] = allow_user
