import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowMacWithPort(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
        self.__access_name = params.get('access_name', 'an3300')

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
            tn.write(("admin\r\n").encode('utf-8'))
            tn.write(("an3300\r\n").encode('utf-8'))
            tn.write("cd fdb\r\n")
            tn.write("sh fdb slot {0}\r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            result = tn.read_until("stop")
            res = []
            res.append(result)
            for x in range(4):
                if ('to stop' in result):
                    tn.write("\r\n".encode('utf-8'))
                    tn.write("\r\n".encode('utf-8'))
                    tn.write("\r\n".encode('utf-8'))
                    tn.write("\r\n".encode('utf-8'))
                    result.join(result)
                    tn.write("\r\n".encode('utf-8'))

            result = tn.read_until("fdb")
            res.append(result)
            tn.close()
            return res

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return "error"
