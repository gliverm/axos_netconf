"""
Collection of Netconf methods related to vlans
"""

import xmltodict
import jinja2

JENV = jinja2.Environment(autoescape=True)


class NetconfVlanMixin:
    """Netconf Mixin of VLAN related methods"""

    def edit_vlan(
        self,
        vlan_id: int,
        description: str = None,
        mode: str = None,
        l3_service: str = None,
        mac_learning: str = None,
        ont_external_rg: str = None,
        egress_flooding: str = None,
        mcast_bandwidth: str = None,
        source_verify: str = None,
        mff: str = None,
    ):
        """Create/Edit VLAN.
        # TODO add access-group and profile settings
        """

        template = """
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <config xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                        <vlan>
                            <vlan-id>{{vlan_id}}</vlan-id>
                            {% if mode != "None" %}
                            <mode>{{mode}}</mode>
                            {% endif %}
                            {% if description != "None" %}
                            <description>{{description}}</description>
                            {% endif %}
                            {% if l3_service != "None" %}
                            <l3-service>{{l3_service}}</l3-service>
                            {% endif %}
                            {% if mac_learning != "None" %}
                            <mac-learning>{{mac_learning}}</mac-learning>
                            {% endif %}
                            {% if ont_external_rg != "None" %}
                            <ont-external-rg>{{ont_external_rg}}</ont-external-rg>
                            {% endif %}
                            {% if egress_flooding != "None" %}
                            <egress xmlns="http://www.calix.com/ns/exa/access-security">
                                <flooding>{{egress_flooding}}</flooding>
                            </egress>
                            {% endif %}
                            {% if mcast_bandwidth != "None" %}
                            <mcast-bandwidth xmlns="http://www.calix.com/ns/exa/igmp">{{mcast_bandwidth}}</mcast-bandwidth>
                            {% endif %}
                            {% if source_verify != "None" %}
                            <source-verify xmlns="http://www.calix.com/ns/exa/layer2-service-protocols">{{source_verify}}</source-verify>
                            {% endif %}
                            {% if mff != "None" %}
                            <mff xmlns="http://www.calix.com/ns/exa/layer2-service-protocols">{{mff}}</mff>
                            {% endif %}
                        </vlan>
                    </system>
                </config>
            </config>
        """
        template = JENV.from_string(template)
        config = template.render(
            vlan_id=str(vlan_id),
            mode=str(mode),
            description=str(description),
            l3_service=str(l3_service),
            mac_learning=str(mac_learning),
            ont_external_rg=str(ont_external_rg),
            egress_flooding=str(egress_flooding),
            mcast_bandwidth=str(mcast_bandwidth),
            source_verify=str(source_verify),
            mff=str(mff),
        )
        response = self.edit_config(config=config)
        return response

    def get_vlan_details(self, vlan_id: int) -> dict:
        """Get all VLAN configuration details including defaults
        returning a dictionary of data values.
        """

        nc_filter = f"""
            <config xmlns="http://www.calix.com/ns/exa/base">
                <system>
                    <vlan>
                        <vlan-id>{vlan_id}</vlan-id>
                    </vlan>
                </system>
            </config>
        """
        response = self.get_config(nc_filter=("subtree", nc_filter))

        data = {}
        if xmltodict.parse(response.xml)["rpc-reply"]["data"] is not None:
            details = xmltodict.parse(response.xml)["rpc-reply"]["data"]["config"][
                "system"
            ]["vlan"]
            data["vlan_id"] = details["vlan-id"]
            data["mode"] = details["mode"]
            data["description"] = details["description"]
            if "l3-service" in details:
                data["l3_service"] = details["l3-service"]
            if "mac-learning" in details:
                data["mac_learning"] = details["mac-learning"]
            if "ont-external-rg" in details:
                data["ont_external_rg"] = details["ont-external-rg"]
            if "egress" in details:
                data["egress-flooding"] = details["egress"]["flooding"]
            if "mcast-bandwidth" in details:
                data["mcast_bandwidth"] = details["mcast-bandwidth"]["#text"]
            if "source-verify" in details:
                data["source_verify"] = details["source-verify"]["#text"]
            if "mff" in details:
                data["mff"] = details["mff"]["#text"]
        return {"data": data}

    def get_vlan_ids(self) -> dict:
        """Get and return list of all VLAN IDs configured."""

        nc_filter = """
            <config xmlns="http://www.calix.com/ns/exa/base">
                <system>
                    <vlan>
                        <vlan-id/>
                    </vlan>
                </system>
            </config>
        """
        response = self.get_config(nc_filter=("subtree", nc_filter))

        data = {}
        if xmltodict.parse(response.xml)["rpc-reply"]["data"] is not None:
            details = xmltodict.parse(response.xml)["rpc-reply"]["data"]["config"][
                "system"
            ]["vlan"]
            data["vlan_ids"] = []
            if isinstance(details, list):
                for vlan_id in details:
                    data["vlan_ids"].append(vlan_id["vlan-id"])
            else:
                data["vlan_ids"].append(details["vlan-id"])

        return {"data": data}

    def del_vlan(self, vlan_id):
        """Delete VLAN configuraiton."""

        config = f"""
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <config xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                        <vlan xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="delete">
                            <vlan-id>{vlan_id}</vlan-id>
                        </vlan>
                    </system>
                </config>
            </config>
        """
        response = self.edit_config(config=config)
        return response

    def get_status_gpon_ont_simulation_vlans(self):
        """Return gpon-ont-simulation status information."""

        nc_filter = """
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <status xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                    <ont-simulation xmlns="http://www.calix.com/ns/exa/gpon-ont-simulation-base">
                        <vlans>
                        <simvlans/>
                        </vlans>
                    </ont-simulation>
                    </system>
                </status>
            </filter>
        """
        response = self.get(nc_filter=nc_filter)
        data = {}
        if xmltodict.parse(response.xml)["rpc-reply"]["data"] is not None:
            details = xmltodict.parse(response.xml)["rpc-reply"]["data"]["status"][
                "system"
            ]["ont-simulation"]["vlans"]["simvlans"]
            data["simvlans"] = []
            for simvlan in details:
                data["simvlans"].append(simvlan)
        return {"data": data}
