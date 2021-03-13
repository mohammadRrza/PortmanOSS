import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class SetPortProfiles(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
        self.__lineprofile = params.get('new_lineprofile')

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
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.read_until("Password:")
            tn.write("cd qos\r\n")
            tn.write("attach rate-limit profile name {0} interface {1}/{2}".format(self.__lineprofile,
                                                                                   self.port_conditions['slot_number'],
                                                                                   self.port_conditions['port_number']))
            tn.write("\r\n".encode('utf-8'))
            tn.write("end\r\n".encode('utf-8'))
            result = tn.read_until("end")
            tn.close()
            return result

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
