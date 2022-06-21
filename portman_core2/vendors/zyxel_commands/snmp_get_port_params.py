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
        import sys
        from pysnmp.entity.rfc3413.oneliner import cmdgen

        SYSNAME = '1.3.6.1.2.1.1.5.0'

        host = self.__HOST
        snmp_ro_comm = self.__get_snmp_community

        # Define a PySNMP CommunityData object named auth, by providing the SNMP community string
        auth = cmdgen.CommunityData(snmp_ro_comm)

        # Define the CommandGenerator, which will be used to send SNMP queries
        cmdGen = cmdgen.CommandGenerator()

        # Query a network device using the getCmd() function, providing the auth object, a UDP transport
        # our OID for SYSNAME, and don't lookup the OID in PySNMP's MIB's
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            auth,
            cmdgen.UdpTransportTarget((host, 161)),
            cmdgen.MibVariable(SYSNAME),
            lookupMib=False,
        )

        # Check if there was an error querying the device
        if errorIndication:
            sys.exit()

        # We only expect a single response from the host for sysName, but varBinds is an object
        # that we need to iterate over. It provides the OID and the value, both of which have a
        # prettyPrint() method so that you can get the actual string data
        for oid, val in varBinds:
            print(oid.prettyPrint(), val.prettyPrint())
