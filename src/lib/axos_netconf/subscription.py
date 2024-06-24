"""
Netconf subscription related methods (pubsub)
"""

import xmltodict
import copy


class NetconfSubscriptionMixin:
    """These methods globally related to the system"""

    def get_event_stream_list(self) -> dict:
        """Get list of available event streams"""

        get_event_stream_list_rpc_cmd = """
            <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <filter type="subtree">
                    <netconf xmlns="urn:ietf:params:xml:ns:netmod:notification">
                        <streams/>
                    </netconf>
                </filter>
            </get>
        """

        response = self.dispatch(rpc_command=get_event_stream_list_rpc_cmd)

        if response.ok:
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            try:
                streams = xml_dict["data"]["netconf"]["streams"]["stream"]
            except (KeyError, TypeError):
                return self.NetconfResponse(ok=False, err="No streams found")
            return self.NetconfResponse(data={"streams": streams})

        return self.NetconfResponse(ok=response.ok, err=response.err)

    def create_subscription(self, category: str | list | None = None) -> dict:
        """Create a subscription to a exa-events stream returning ok=True if successful.

        Subscription may only be executed once per session.

        Category is an optional filter. If category filter is not specified,
        all events will be sent.

        Category filter values are listed via the AXOS CLI command:
        session notification set-category ?.

        No checking for valid category filter values by the system.

        Using a category filter with no matching notifications will
        result in no notifications being recieved.
        """

        create_subscription_rpc_cmd = """
                <create-subscription
                    xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
                        <stream>exa-events</stream>
                </create-subscription>
        """

        categories = []
        if type(category) == str:
            categories = [category]
        if type(category) == list:
            categories = copy.deepcopy(category)

        if len(categories) > 0:
            for idx, category in enumerate(categories):
                categories[idx] = f"category='{category}'"
            categories = " or ".join(categories)
            create_subscription_rpc_cmd = f"""
                    <create-subscription
                        xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
                            <stream>exa-events</stream>
                            <filter
                                xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0"
                                type="xpath"
                                select="/*[{categories}]"
                                />
                    </create-subscription>
            """

        response = self.dispatch(rpc_command=create_subscription_rpc_cmd)

        if response.ok:
            return self.NetconfResponse()

        return self.NetconfResponse(ok=False, err=response.err)

    def take_notification(self, block: bool = False, timeout: int | None = 30) -> dict:
        """Take a notification from the stream.
        Returning response.data = None if no notification is available.
        """

        block = True if block else False
        response = self.take_session_notification(block=block, timeout=timeout)

        if response.ok:
            if response.xml is None:
                return self.NetconfResponse(data=None)
            xml_dict = xmltodict.parse(response.xml)["notification"]
            if "@xmlns" in xml_dict:
                del xml_dict["@xmlns"]
            return self.NetconfResponse(data=xml_dict)

        return self.NetconfResponse(ok=False, err=response.err)
