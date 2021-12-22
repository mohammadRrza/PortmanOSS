import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class SysSnmpGetCommunity(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__snmp_name = params['snmp_name']
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

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.read_until(b"Password:")
            tn.write("sys snmp getcommunity {0}\r\n\r\n".format(self.__snmp_name).encode('utf-8'))
            time.sleep(1)
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('*************************************')
            print(("add get snmp community {0}".format(self.__snmp_name)))
            print('*************************************')
            return dict(result="add get snmp community {0}".format(self.__snmp_name), status=200)

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
