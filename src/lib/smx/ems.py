"""
Collection of SMx EMS Rest API methods.
"""


class SmxEmsMixin:
    def create_ems_profile_class_map(self, data):
        """Create class map on EMS."""
        # Class Map is created at the EMS level does not go to devices
        # TODO Create model schema for data from swagger doc
        # Consider using /config/device route instead
        route = f"/ems/profile/class-map"
        return self.post(route, data)

    def create_ems_profile_subscriber_service_template(self, data):
        """Create service template"""
        # TODO Create model schema for data from swagger doc
        # Consider using /config/device route instead
        route = f"/ems/profile/subscriber-service-template"
        return self.post(route, data)

    def create_ems_profile_policy_map(self, data):
        """Create service template"""
        # TODO Create model schema for data from swagger doc
        # Consider using /config/device route instead
        route = f"/ems/profile/policy-map"
        return self.post(route, data)
