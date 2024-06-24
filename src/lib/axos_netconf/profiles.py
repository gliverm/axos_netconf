"""
Collection of Netconf methods related to profiles
"""

import xmltodict
import jinja2

JENV = jinja2.Environment(autoescape=True)


class NetconfProfilesMixin:
    """Netconf Mixin of Profile related methods"""

    def get_class_map(self) -> dict:
        """Get all class map profiles"""

        # type = type.str().lower()
        nc_filter = """
            <config xmlns="http://www.calix.com/ns/exa/base">
                <profile>
                    <class-map/>
                </profile>
            </config>
        """

        response = self.get_config(nc_filter=("subtree", nc_filter))

        data = {}
        if xmltodict.parse(response.xml)["rpc-reply"]["data"] is not None:
            details = xmltodict.parse(response.xml)["rpc-reply"]["data"]["config"][
                "profile"
            ]

        return {"data": data}


# Get ethernet class maps
# #482
# <nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:51b699d5-61e4-4b26-8c67-5e0444c37aa8">
#   <nc:get-config>
#     <nc:source>
#       <nc:running/>
#     </nc:source>
#     <nc:filter>
#       <config xmlns="http://www.calix.com/ns/exa/base">
#         <profile>
#           <class-map>
#             <ethernet/>
#           </class-map>
#         </profile>
#       </config>
#     </nc:filter>
#     <ns0:with-defaults xmlns:ns0="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">report-all</ns0:with-defaults>
#   </nc:get-config>
# </nc:rpc>
