"""
Collection of Netconf methods related to interfaces
"""

import xmltodict


class NetconfInterfacesMixin:
    """Netconf Mixin of Interface related methods"""

    def getcfg_pon_enabled(self, name) -> dict | None:
        """Get the enable state of the PON interfaces"""
        # Filter to obtain single PON port admin state
        nc_filter = f"""
            <interfaces
                xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>{name}</name>
                    <type
                        xmlns:gpon-std="http://www.calix.com/ns/exa/gpon-interface-std">gpon-std:pon
                    </type>
                    <enabled></enabled>
                </interface>
            </interfaces>
        """

        response = self.get_config(nc_filter=("subtree", nc_filter))
        data = xmltodict.parse(response.xml)["rpc-reply"]["data"]
        if xmltodict.parse(response.xml)["rpc-reply"]["data"] is None:
            return None
        details = xmltodict.parse(response.xml)["rpc-reply"]["data"]["interfaces"][
            "interface"
        ]

        return details

    def editcfg_pon_enabled(self, name, state):
        """Edit the enable state of the PON interfaces"""

        config = f"""
            <config
                xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <interfaces
                    xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>{name}</name>
                        <type
                            xmlns:gpon-std="http://www.calix.com/ns/exa/gpon-interface-std">gpon-std:pon
                        </type>
                        <enabled>{state}</enabled>
                    </interface>
                </interfaces>
            </config>
        """
        response = self.edit_config(config=config)
        return response
