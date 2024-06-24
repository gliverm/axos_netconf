"""
AXOS collection of netconf functions organized for a workflow.
Workflows re-use the core netconf commands into logical groupings
of commands to perform workflow tasks.

Command prefix: wf

"""

import enum


class Pattern(enum.Enum):
    SCALECURRENT = "SCALECURRENT"
    SCALEFUTURE = "SCALEFUTURE"


def _get_s_vlan_pattern_attributes(pattern) -> dict:
    """Get VLAN parameters needed to create S-VLAN configurations for scale systems.
    Valid patterns are : SCALECURRENT, SCALEFUTURE
    # TODO Should reside in a helper function
    """
    # S-VLAN Allocation for 8 cards 2/1 thru 5/2 all with 16 pon ports each
    data = {}
    if pattern in ["SCALECURRENT", "SCALEFUTURE"]:
        shelf_range = range(2, 5 + 1)
        card_range = range(1, 2 + 1)
        port_range = range(1, 16 + 1)
        data["vlan_attributes"] = []
        for shelf in shelf_range:
            for card in card_range:
                for port in port_range:
                    if pattern == "SCALECURRENT":
                        vlan_id = f"{card}{shelf}{port:02d}"
                    if pattern == "SCALEFUTURE":
                        vlan_id = f"{card}{shelf}{port + 20:02d}"
                    data["vlan_attributes"].append(
                        {
                            "vlan_id": int(vlan_id),
                            "description": f"s-vlan on port {shelf}/{card}/xp{port}",
                            "mode": "ONE2ONE",
                        }
                    )
    return data


def wf_edit_bulk_s_vlan_for_scale(self, pattern: Pattern):
    """Build S-VLANs on scale system according to pre-determined pattern."""
    vlans = _get_s_vlan_pattern_attributes("SCALECURRENT")
    for vlan in vlans["vlan_attributes"]:
        ok = conn.edit_vlan(**vlan)
        if ok:
            LOGGER.info(f"vlan {vlan['vlan_id']} configured")
