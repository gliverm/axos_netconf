"""
Module is the base file mixing together all Netconf related operations.

Design choices:
*   Session based using core set of session operations
*   Intended for E9 AXOS device
*   Netconf methods logically grouped into separate files
*   Netconf method development based on specific use-case first to address
        in some cases more effecient use
*   Combining Netconf operations into work flows is responsibility of calling app
*   Netconf parameter naming match netconf/cli naming exchanging hyphen for underscore
*   Parameter type checking done at target and not within code
*   editcfg parameters that default to None are considered optional
*   editcfg parameters without defaults considered required
*   use default Jinja2 environment

Opportunities for improvement:
* Consider separating templates out into a directory of templates
* Consider better modeling for responses
* Consider making commands more consistent by using dictionaries of parameters
* Implement data modeling
* Improved error checking

"""

from lib.axos_netconf.session import NetconfSessionMixin
from lib.axos_netconf.vlan import NetconfVlanMixin
from lib.axos_netconf.interfaces import NetconfInterfacesMixin
from lib.axos_netconf.profiles import NetconfProfilesMixin
from lib.axos_netconf.ont import NetconfONTMixin
from lib.axos_netconf.responses import NetconfResponse
from lib.axos_netconf.subscription import NetconfSubscriptionMixin
from lib.axos_netconf.system import NetconfSystemMixin


# Session class listed as last mixin
class NetconfSession(
    NetconfProfilesMixin,
    NetconfVlanMixin,
    NetconfInterfacesMixin,
    NetconfONTMixin,
    NetconfSubscriptionMixin,
    NetconfSystemMixin,
    NetconfSessionMixin,
):
    """Base Netconf class mixing in methods from other files."""

    class NetconfResponse(NetconfResponse):
        """Model for all session returns."""
