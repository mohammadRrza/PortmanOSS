from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from .command_base import BaseCommand
import re
from .create_profile import CreateProfile
import telnetlib
import time
from socket import error as socket_error
from pysnmp.hlapi import *


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

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in nextCmd(SnmpEngine(),
                                  CommunityData(self.__get_snmp_community, mpModel=0),
                                  UdpTransportTarget((self.__HOST, self.__snmp_port)),
                                  ContextData(),
                                  ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'))):
            if errorIndication or errorStatus:
                print(errorIndication or errorStatus)
                break
            else:
                for varBind in varBinds:
                    print(' = '.join([x.prettyPrint() for x in varBind]))
