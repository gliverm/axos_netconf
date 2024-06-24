"""
Collection of Netconf methods related to system level operations.
"""

import xmltodict
from lib.axos_netconf.responses import NetconfResponse


class NetconfSystemMixin:
    """Netconf Mixin of System Level methods."""

    def getcfg_system_location(self):
        """Get the system location."""
        nc_filter = """
            <config xmlns="http://www.calix.com/ns/exa/base">
                <system>
                    <location/>
                </system>
            </config>
        """
        response = self.get_config(nc_filter=("subtree", nc_filter))
        if response.ok:
            location = xmltodict.parse(response.xml)["rpc-reply"]["data"]["config"][
                "system"
            ]["location"]
            return NetconfResponse(
                ok=True,
                err=response.error,
                data={"location": location},
                xml=response.xml,
            )
        else:
            return NetconfResponse(ok=False, err=response.error)

    def editcfg_system_location(self, location):
        """Edit the system location."""

        config = f"""
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <config xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                        <location>{location}</location>
                    </system>
                </config>
            </config>
        """
        response = self.edit_config(config=config)
        if response.ok:
            return NetconfResponse(ok=response.ok)
        else:
            return NetconfResponse(ok=response.ok, err=response.error)
