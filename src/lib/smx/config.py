"""
Collection of SMx Rest API methods.
"""


class SmxConfigMixin:
    def get_config_device_name(self, device_name):
        """Return device by node name"""
        route = f"/config/device/{device_name}"
        return self.get(route)
