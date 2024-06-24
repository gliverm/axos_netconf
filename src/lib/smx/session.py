"""
The intent of this module is to be a collection of SMx REST
API functions against an E9 AXOS device.  

Design choices:
* modeling not implemented - may reconsider when reasonable

TODO Refactor this so that NetconfSession is a base class and re-usable
TODO Refactor to include modeling for results expectations
TODO Better variable checking on init 
"""

import requests

# Suppress SSL certificate verification errors
requests.packages.urllib3.disable_warnings()


class SmxRestSessionMixin:
    """Class to represent a SMX Rest"""

    def __init__(self, hostname, apiport, apiroot, username, password):
        self.hostname = hostname
        self.apiport = apiport
        self.apiroot = apiroot
        self.username = (
            username  # String up to 48 chars, letters numbers, underscore, hyphen, dot
        )
        self.password = (
            password  # String 3 to 48 chars, letters numbers, underscore, hyphen, dot
        )
        self.session = None

    def __get_root(self):
        """Return api root url"""
        return f"https://{self.hostname}:{self.apiport}{self.apiroot}"

    def __get_url(self, route):
        """Return api url"""
        return self.__get_root() + route

    def get(self, route):
        """HTTP Get function to send REST APIs"""
        # TODO add ability to use filter and params
        if self.session is None:
            self.connect()

        url = self.__get_url(route)
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        # TODO Consider creating response model
        return response.json()

    def post(self, route, data):
        """HTTP POST function to mainly used to create.
        Consider data as json to be dump to string or used as-is.
        """
        # data = json.dumps(data)
        if self.session is None:
            self.connect()

        url = self.__get_url(route)
        response = self.session.post(url, data, verify=False)
        response.raise_for_status()
        return response

    def put(self, route, data):
        """HTTP PUT function used to update.
        Consider data as json to be dump to string or used as-is.
        """
        # data = json.dumps(data)
        if self.session is None:
            self.connect()

        url = self.__get_url(route)
        response = self.session.put(url, data, verify=False)
        response.raise_for_status()
        return response

    def delete(self, route, data={}, params={}):
        """HTTP DELETE function used to delete objects."""
        if self.session is None:
            self.connect()

        url = self.__get_url(route)
        response = self.session.delete(url, params, data, verify=False)
        response.raise_for_status()
        return response

    def connect(self):
        """Attempt to establish REST session."""
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def close(self):
        """Close the requests session."""
        if self.session is not None:
            self.session.close()
            self.session = None
