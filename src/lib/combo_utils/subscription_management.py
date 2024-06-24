"""
File: subscription_management.py
Author: Ben Wilson

Description: Houses the subscription_manager class, instances of which
can be used to listen for subscription events on an AXOS system.
The subscription manager requires a NETCONF connection to the AXOS system
you want notifications from, this connection can be one already in use
by other toolbox functions but this may not be ideal if you plan to change
the filters of the subscription.
"""

import threading
from app.base_logger import getlogger
from app.lib.axos_netconf.base import NetconfSession
from pubsub import pub

LOGGER = getlogger(__name__)


class SubscriptionManager:
    """
    Used to create a subscription on an AXOS system over NETCONF.

    Listens for notifications in the background of other code
    and using pubsub library publishes a message containing the
    notification data allowing the user to create subscription
    functions in their code to parse the data.
    """

    def __init__(
        self,
        conn: NetconfSession,
        name: str,
        notifCategories: str | list | None = None,
    ):
        self.conn = conn
        self.name = name
        self.enabled = True
        self.notification_categories = self._format_notification_categories(
            notifCategories
        )
        self._prev_notification_categories = None

        self.update_subscription(restart_conn=False)  # create initial subscription

    def _format_notification_categories(
        self, notifCategories: str | list | None
    ) -> list | None:
        """Converts notification categories to a list or None type."""
        if type(notifCategories) is str:
            notifCategories.replace(" ", "")  # remove all spaces from string
            return notifCategories.split(",")  # if string is a comma seperated list
        elif type(notifCategories) is list and len(notifCategories) == 0:
            return None
        else:
            return notifCategories

    def update_subscription(self, restart_conn=True):
        """
        Update the subscription categories by resetting the netconf connection
        and creating a new subscription using the contents of the
        notification_categories property.

        (WARNING: Doing this resets the NETCONF connection
        the subscription_manager instance is using!!!)
        """
        # Reset the subscription categories by disconnecting and reconnecting
        if restart_conn:
            self.conn.disconnect()  # disconnect the netconf session
            self.conn.connect()  # reconnect the netconf session
        # Create the new subscription with the updated notification categories
        response = self.conn.create_subscription(self.notification_categories)
        if not response.ok:
            LOGGER.critical(
                f"Failed to create exa-event subscription with notifCategories:\
                 {self.notification_categories}"
            )
            if response.err:
                LOGGER.critical(f"{self.conn.devicename}: {response.err}")
            # revert to previous categories on failure
            self.notification_categories = self._prev_notification_categories
            self._prev_notification_categories = None
            self.update_subscription()
        else:
            self.start_listener()

    def add_notification_categories(self, newCategories: str | list):
        """
        Add new categories to the subscription filter.
        (To apply the changes run the update_subscription method.)
        """
        self._prev_notification_categories = (
            self.notification_categories
        )  # back up previous categories
        # create blank list if no categories were present
        if self.notification_categories is None:
            self.notificiation_categories = []
        newCategories = self._format_notification_categories(newCategories)
        self.notification_categories += (
            newCategories  # add the subscriptions to the existing ones
        )

    def start_listener(self):
        # create and start the notification listener thread
        self.notification_listener = threading.Thread(target=self._listener)
        self.notification_listener.daemon = True
        self.notification_listener.start()

    def stop_listener(self):
        self.notification_listener.stop()

    def remove_notification_categories(self, categoriesToRemove: str | list):
        """
        Remove existing categories from the subsciption filter
        """
        self._prev_notification_categories = (
            self.notification_categories
        )  # back up previous categories
        categoriesToRemove = self._format_notification_categories(categoriesToRemove)
        # remove category from list
        for category in categoriesToRemove:
            self.notification_categories.remove(category)
        # recreate the subscription with the updated categories
        self.update_subscription()

    def get_current_notification_categories(self) -> list:
        return self.notification_categories

    def _listener(self):
        while self.enabled:
            response = self.conn.take_notification(block=True, timeout=None)
            if response.ok and response.data:
                # print(response.data)  # for debugging
                pub.sendMessage(self.name, notif_data=response.data)
