"""
Collection of SMx Rest API methods.
"""


class SmxFaultMixin:
    def get_fault_alarm_count(self):
        """Return active alarm count"""
        route = "/fault/alarm-count"
        return self.get(route)
