import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class PortPvcSet(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_indexes = params.get('port_indexes')
        self.__vpi = params.get('vpi', '0')
        self.__vci = params.get('vci', '35')
        self.__profile = params.get('profile', 'DEFVAL')
        self.__mux = params.get('mux', 'llc')
        self.__vlan_id = params.get('vlan_id', '1')
        self.__priority = params.get('priority', '0')
        self.device_ip = params.get('device_ip')

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
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.read_until(b"Password:")
            for port_item in self.__port_indexes:
                tn.write("port pvc set {0}-{1}-{2}/{3} {4} {5} {6} {7}\r\n\r\n".format(
                    port_item['slot_number'], port_item['port_number'],
                    self.__vpi,
                    self.__vci,
                    self.__profile,
                    self.__mux,
                    self.__vlan_id,
                    self.__priority
                ).encode('utf-8'))
            time.sleep(1)
            tn.write(b"config save")
            time.sleep(1)
            tn.write(b"end\r\n")
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('***********************************************')
            print(("port pvc set 0/35 DEFVAL llc  1 0 for {0}".format(self.__port_indexes)))
            print('***********************************************')
            return dict(result="ports pvc set is done ", port_indexes=self.__port_indexes, status=200)
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
