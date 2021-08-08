import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re
import sys, os

class ShowShelf(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__vlan_name = params.get('vlan_name')
        self.__access_name = params.get('access_name', 'an3300')
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

    retry = 1

    def run_command(self):
        try:
            print("test")
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write(b'admin\r\n')
            tn.write(b'an3300\r\n')
            tn.write(b"cd device\r\n")
            tn.write(b"show slot\r\n\r\n")
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            time.sleep(0.5)
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            return str(result)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
