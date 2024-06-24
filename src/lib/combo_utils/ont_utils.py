"""
File: ONT_arrive_depart_monitor.py
Author: Ben Wilson (Associate Solutions Test Engineer)

Description:
Houses various higher level functions that can be used in relation to ONTs

"""

import threading
import time
import re

from app.base_logger import getlogger
from app.lib.axos_netconf.base import NetconfSession

LOGGER = getlogger(__name__)


def is_pon_port(string: str) -> bool:
    """Checks if the entered string is a PON port
    Valid format = [1-9]/[1-2]/xp[1-48]
    """
    # ponport_regex = re.compile(r"^[1-9]\/[1-2]\/xp([1-9]{1,2})$")
    ponport_regex = re.compile(r"^[1-9]\/[1-2]\/[xg]p([1-9]{1,2})$")
    match = ponport_regex.match(string)
    if not match:
        return False
    if int(match.group(1)) > 48:
        return False
    return True


def get_discovered_onts(conn: NetconfSession, format: type = list) -> list | dict:
    """Get the current discovered onts and return them as a list or dictionary"""
    response = conn.get_discovered_onts()
    if response.err:
        LOGGER.critical(f"Error fetching discovered ONTs: {response.err}")
        return None
    onts = []
    if not response.data:
        LOGGER.critical("No ONTs discovered on system")
        return None
    retrieved_onts = response.data["discovered onts"]
    if (
        type(retrieved_onts) is dict
    ):  # single upgrade class (upgrade_classes_data is a dict)
        onts.append(retrieved_onts)
    else:  # multiple upgrade classes (upgrade_classes_data is a list)
        onts = retrieved_onts
    if format is list:
        return onts
    elif dict:
        return ont_list2dict(conn, onts)


def get_ont_states(
    conn: NetconfSession, format: list | dict = list
) -> list | dict | None:
    response = conn.get_ont_states()
    if response.err:
        LOGGER.critical(f"Error fetching discovered ONTs: {response.err}")
    ont_statuses = []
    if not response.data:
        LOGGER.critical("No ONTs discovered on system")
    retrieved_statuses = response.data["states"]
    if (
        type(retrieved_statuses) is dict
    ):  # single upgrade class (upgrade_classes_data is a dict)
        ont_statuses.append(retrieved_statuses)
    else:  # multiple upgrade classes (upgrade_classes_data is a list)
        ont_statuses = retrieved_statuses
    if format is list:
        return ont_statuses
    elif dict:
        return ont_list2dict(conn, ont_statuses)


def ont_list2dict(conn: NetconfSession, ont_list: list) -> dict:
    """
    Convert a list of discovered ONTs into a dictionary
    that uses the IDs as keys.
    """
    ont_dict = {}
    for ont in ont_list:
        ont_dict[ont["ont-id"]] = ont
        del ont_dict[ont["ont-id"]]["ont-id"]
    return ont_dict


def ont_ports_to_ids(conn: NetconfSession, id_list: list) -> list:
    discovered_onts = get_discovered_onts(conn, format=list)
    new_id_list = id_list[:]
    for id in id_list:
        if is_pon_port(id):
            index = new_id_list.index(id)
            new_id_list.remove(id)
            for ont in discovered_onts:
                if f"{ont['shelf-id']}/{ont['slot-id']}/{ont['pon-port']}" == id:
                    new_id_list.insert(index, ont["ont-id"])
    return new_id_list
