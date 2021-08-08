import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class ShowProfiles(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__vlan_name = params.get('vlan_name')
        self.__access_name = params.get('access_name','an3300')
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


    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write('{0}\r\n'.format("admin").encode('utf-8'))
            tn.write('{0}\r\n'.format(self.__access_name).encode('utf-8'))
            tn.write(b"cd profile\r\n")
            tn.write(b"show all dsl-profile-name\r\n")
            result1 = tn.read_until(b"--Press any key to continue Ctrl+c to stop--")
            tn.write(b"\r\n")
            result2 = tn.read_until(b"number")
            result = result1+result2
            tn.close()
            return str(result)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
