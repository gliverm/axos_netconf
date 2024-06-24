"""
Collection of Netconf methods related to ONTs
"""

import xmltodict
import jinja2
from lib.axos_netconf.responses import NetconfResponse


JENV = jinja2.Environment(autoescape=True)


class NetconfONTMixin:
    """Netconf Mixin of ONT related methods"""

    def get_ont_operating_status(self, ontid) -> NetconfResponse:
        """
        Gets the operating status of the passed ONT (present, missing, or not-linked)
        and returns it as a string.
        """

        nc_filter = f"""
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <status xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                        <ont xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                            <ont-id>{ontid}</ont-id>
                            <status>
                                <oper-state/>
                            </status>
                        </ont>
                    </system>
                </status>
            </filter>
        """
        response = self.get(nc_filter)

        if response.ok:
            oper_status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            try:
                if "status" in xml_dict["data"]["status"]["system"]["ont"].keys():
                    oper_status = xml_dict["data"]["status"]["system"]["ont"]["status"][
                        "oper-state"
                    ]
                else:
                    oper_status = None
                return NetconfResponse(data={"status": oper_status})
            except (KeyError, TypeError):
                oper_status = None
                return NetconfResponse(data={"status": oper_status})
        else:
            return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_reboot_by_ontid(self, ontid) -> NetconfResponse:
        """Execute the 'perform ont reboot' command via netconf.
        id may be composed of: uppercase, lowercase, letters, digits, -, _
        YANG Modules: gpon-interface-exec-base, gpon-interface-base
        """

        rpc_command = f"""
            <perform-ont-reboot-by-ontid xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                <ont-id>{ontid}</ont-id>
            </perform-ont-reboot-by-ontid>
        """
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "status" in xml_dict:
                status = xml_dict["status"]["#text"]
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_reboot_by_pon(self, port) -> NetconfResponse:
        """Execute the 'perform ont reboot pon' command via netconf.
        YANG Modules: gpon-interface-exec-base, gpon-interface-base
        """

        rpc_command = f"""
            <perform-ont-reboot-by-pon xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                <port>{port}</port>
            </perform-ont-reboot-by-pon>
        """
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
            # TODO Investigate this data value not being used
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_reboot_by_serial(self, vendorid, serial) -> NetconfResponse:
        """Execute the 'perform ont reboot serial-number' command via netconf.
        YANG Modules: gpon-interface-base
        """

        rpc_command = f"""
            <perform-ont-reboot-by-serialnumber xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                <serial-number>{serial}</serial-number>
                <vendor-id>{vendorid}</vendor-id>
            </perform-ont-reboot-by-serialnumber>
        """
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
            # TODO Investigate this data value not being used
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_upgrade_install(
        self,
        release_name,
        directory_path,
        upgrade_class,
        download="NO",
        force_reinstall="NO",
    ) -> NetconfResponse:
        """
        Execute the 'ont-upgrade ont-install' command via netconf.
        YANG Module: ont-upgrade
        """

        template = """
            <ont-install xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                <release-name>{{release_name}}</release-name>
                <directory-path>{{directory_path}}</directory-path>
                {% if upgrade_class != "None" %}
                <class>{{upgrade_class}}</class>
                {% endif %}
                <download>{{download}}</download>
                <force-reinstall>{{force_reinstall}}</force-reinstall>
            </ont-install>
        """
        template = JENV.from_string(template)

        rpc_command = template.render(
            release_name=str(release_name),
            directory_path=str(directory_path),
            upgrade_class=str(upgrade_class),
            download=str(download),
            force_reinstall=str(force_reinstall),
        )
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_upgrade_download(
        self, release_name, upgrade_class
    ) -> NetconfResponse:
        """
        Execute the 'ont-upgrade ont-download' command via netconf
        """

        template = """
            <ont-download xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                <release-name>{{release_name}}</release-name>
                {% if mode != "None" %}
                <class>{{upgrade_class}}</class>
                {% endif %}
            </ont-download>
        """
        template = JENV.from_string(template)

        rpc_command = template.render(
            release_name=str(release_name), upgrade_class=str(upgrade_class)
        )
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_upgrade_activate(
        self, release_name, upgrade_class=None
    ) -> NetconfResponse:
        """
        Execute the 'ont-upgrade ont-activate' command via netconf
        """

        template = """
            <ont-activate xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                <release-name>{{release_name}}</release-name>
                {% if mode != "None" %}
                <class>{{upgrade_class}}</class>
                {% endif %}
            </ont-activate>
        """
        template = JENV.from_string(template)

        rpc_command = template.render(
            release_name=str(release_name), upgrade_class=str(upgrade_class)
        )
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def perform_ont_upgrade_commit(
        self, release_name, upgrade_class
    ) -> NetconfResponse:
        """
        Execute the 'ont-upgrade ont-commit' command via netconf
        """
        template = """
            <ont-commit xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                <release-name>{{release_name}}</release-name>
                {% if mode != "None" %}
                <class>{{upgrade_class}}</class>
                {% endif %}
            </ont-commit>
        """
        template = JENV.from_string(template)

        rpc_command = template.render(
            release_name=str(release_name), upgrade_class=str(upgrade_class)
        )
        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
            return NetconfResponse(data={"status": status})

        return NetconfResponse(ok=response.ok, err=response.err)

    def get_ont_upgrade_card_statuses(self) -> NetconfResponse:
        rpc_command = """
            <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <filter>
                <status xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                    <ont-upgrade xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                        <status>
                        <card>
                            <card/>
                            <time/>
                            <status/>
                        </card>
                        </status>
                    </ont-upgrade>
                    </system>
                </status>
                </filter>
            </get>
        """

        response = self.dispatch(rpc_command=rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            try:
                card_statuses = xml_dict["data"]["status"]["system"]["ont-upgrade"][
                    "status"
                ]["card"]
                return NetconfResponse(data={"statuses": card_statuses})
            except (KeyError, TypeError):
                card_statuses = None
        return NetconfResponse(ok=response.ok, err=response.err)

    def edit_ont_upgrade_server(self, hostname, username, password) -> NetconfResponse:
        # check for an existing hostname and remove it
        # if different from the inputted hostname
        check_hostname_rpc_command = """
            <get-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <source>
                <running/>
                </source>
                <filter>
                <config xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                    <ont-upgrade xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                        <server>
                        <hostname/>
                        </server>
                    </ont-upgrade>
                    </system>
                </config>
                </filter>
            </get-config>
        """
        response = self.dispatch(rpc_command=check_hostname_rpc_command)
        if not response.ok or response.err:
            return NetconfResponse(ok=response.ok, err=response.err)
        else:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            try:
                previous_hostname = xml_dict["data"]["config"]["system"]["ont-upgrade"][
                    "server"
                ]["hostname"]
            except (KeyError, TypeError):
                previous_hostname = None
            # if there is an existing hostname that differs from the one passed delete the existing one
            if previous_hostname and not hostname == previous_hostname:
                del_hostname_rpc_command = f"""
                    <edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <target>
                        <running/>
                        </target>
                        <config>
                        <config xmlns="http://www.calix.com/ns/exa/base">
                            <system>
                            <ont-upgrade xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                                <server xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="delete">
                                <hostname>{previous_hostname}</hostname>
                                </server>
                            </ont-upgrade>
                            </system>
                        </config>
                        </config>
                    </edit-config>
                """
                response = self.dispatch(rpc_command=del_hostname_rpc_command)

                if not response.ok or response.err:
                    return NetconfResponse(ok=response.ok, err=response.err)

        edit_config_rpc_command = f"""
            <edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <target>
                <running/>
                </target>
                <config>
                <config xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                    <ont-upgrade xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                        <server xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="replace">
                        <hostname>{hostname}</hostname>
                        <username nc:operation="replace">{username}</username>
                        <password nc:operation="replace">{password}</password>
                        </server>
                    </ont-upgrade>
                    </system>
                </config>
                </config>
            </edit-config>
        """

        response = self.dispatch(rpc_command=edit_config_rpc_command)

        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["status"]["#text"]
                return NetconfResponse(data={"status": status})
        else:
            return NetconfResponse(ok=response.ok, err=response.err)

    def get_upgrade_server_status(self) -> NetconfResponse:
        """
        Get a response from the device containing the ONT-upgrade FTP server status
        """
        rpc_command = """
            <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <filter>
                <status xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                    <ont-upgrade xmlns="http://www.calix.com/ns/exa/ont-upgrade">
                        <server>
                        <status/>
                        </server>
                    </ont-upgrade>
                    </system>
                </status>
                </filter>
            </get>
        """
        response = self.dispatch(rpc_command=rpc_command)
        status = None
        if response.ok:
            try:
                xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
                status = xml_dict["data"]["status"]["system"]["ont-upgrade"]["server"][
                    "status"
                ]
                return NetconfResponse(data={"status": status})
            except (KeyError, TypeError):
                status = None
        return NetconfResponse(ok=response.ok, err=response.err)

    def get_ont_upgrade_classes(self) -> NetconfResponse:
        """
        Return a response containing the ONT-upgrade classes on the system
        """
        rpc_command = """
            <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <filter>
                <config xmlns="http://www.calix.com/ns/exa/base">
                    <system>
                    <ont-upgrade-class xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                        <name/>
                    </ont-upgrade-class>
                    </system>
                </config>
                </filter>
            </get>
        """

        response = self.dispatch(rpc_command=rpc_command)
        if response.ok:
            status = None
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                data = xml_dict["data"]
                return NetconfResponse(data=data)

        return NetconfResponse(ok=response.ok, err=response.err)

    def get_discovered_onts(self) -> NetconfResponse:
        rpc_command = """
        <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <filter>
        <status xmlns="http://www.calix.com/ns/exa/base">
            <system>
            <ont-linkages xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                <ont-linkage>
                <ont-id/>
                <shelf-id/>
                <slot-id/>
                <pon-port/>
                <state/>
                </ont-linkage>
                <ont-count/>
            </ont-linkages>
            </system>
        </status>
        </filter>
        </get>
        """

        response = self.dispatch(rpc_command=rpc_command)
        if response.ok:
            xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
            if "data" in xml_dict:
                discovered = xml_dict["data"]["status"]["system"]["ont-linkages"][
                    "ont-linkage"
                ]
                return NetconfResponse(data={"discovered onts": discovered})

        return NetconfResponse(ok=response.ok, err=response.err)

    def get_ont_states(self) -> NetconfResponse:
        rpc_command = """
        <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <filter>
            <status xmlns="http://www.calix.com/ns/exa/base">
                <system>
                <ont xmlns="http://www.calix.com/ns/exa/gpon-interface-base">
                    <ont-id/>
                    <status>
                    <oper-state/>
                    </status>
                </ont>
                </system>
            </status>
            </filter>
        </get>
        """

        response = self.dispatch(rpc_command=rpc_command)
        if response.ok:
            try:
                xml_dict = xmltodict.parse(response.xml)["rpc-reply"]
                states = xml_dict["data"]["status"]["system"]["ont"]
                return NetconfResponse(data={"states": states})
            except (KeyError, TypeError):
                status = None
        return NetconfResponse(ok=response.ok, err=response.err)
