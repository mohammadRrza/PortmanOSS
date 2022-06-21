from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from .command_base import BaseCommand
import re
from .create_profile import CreateProfile
import telnetlib
import time
from socket import error as socket_error


class SNMPGetPortParam(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.params = params
        self.__telnet_username = None
        self.__telnet_password = None
        self.__ADSL_UPSTREAM_SNR = params.get('adsl_upstream_snr_oid')
        self.__port_indexes = params.get('port_indexes')
        self.__snmp_port = params.get('snmp_port', 161)
        self.__snmp_timeout = params.get('snmp_timeout', 7)
        self.__lineprofile = params.get('new_lineprofile')
        self.__get_snmp_community = params.get('get_snmp_community')
        self.device_ip = params.get('device_ip')
        self.port_conditions = params.get('port_conditions')

    @property
    def HOST(self):
        return self.__HOST

    @HOST.setter
    def HOST(self, value):
        self.__HOST = value

    @property
    def telnet_username(self):
        return self.__telnet_username

    @telnet_username.setter
    def telnet_username(self, value):
        self.__telnet_username = value

    @property
    def telnet_password(self):
        return self.__telnet_password

    @telnet_password.setter
    def telnet_password(self, value):
        self.__telnet_password = value

    def __clear_port_name(self, port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern, port_name, re.M | re.DOTALL)
        return st.group()

    retry = 1

    def run_command(self):
        print(self.__get_snmp_community)
        target_oids_value = []
        self.__port_indexes = [{'port_index': '{}.{}'.format(self.port_conditions['slot_number'],
                                                            self.port_conditions['port_number'])}]

        for index, port_item in enumerate(self.__port_indexes, 1):
            target_oids_value.append(('.{0}.{1}'.format(self.__ADSL_UPSTREAM_SNR, port_item['port_index']),
                                      rfc1902.OctetString(self.__ADSL_UPSTREAM_SNR)))
            if index % 40 == 0 or index == len(self.__port_indexes):
                target_oids_value_tupple = tuple(target_oids_value)
                cmd_gen = cmdgen.CommandGenerator()

                error_indication, error_status, error_index, var_binds = cmd_gen.getCmd(
                    cmdgen.CommunityData(self.__get_snmp_community),
                    cmdgen.UdpTransportTarget((self.__HOST, self.__snmp_port), timeout=self.__snmp_timeout, retries=2),
                    *target_oids_value_tupple
                )
                target_oids_value = []

                # Check for errors and print out results
                if error_indication:
                    raise Exception(error_indication)
                else:
                    if error_status:
                        error_desc = "error: {0} send to port {1}!!!. dslam dont have line profile {2}".format(
                            error_status.prettyPrint(), port_item['port_index'], self.__lineprofile)
        return {"result": "ports line profile changed to {0}".format(self.__lineprofile),
                "port_indexes": self.__port_indexes}
