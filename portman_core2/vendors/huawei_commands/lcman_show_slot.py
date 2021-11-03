import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class LcmanShowSlot(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__slot = params['slot']
        self.device_ip = params.get('device_ip')

    @property
    def HOST(self):
        return self.__HOST

    @HOST.setter
    def HOST(self, value):
        self.__HOST = value

    @property
    def port_name(self):
        return self.__port_name

    @port_name.setter
    def port_name(self, value):
        self.__port_name = self.__clear_port_name(value)

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
            if tn.read_until('>>User name:'):
                tn.write((self.__telnet_username + "\n").encode('utf-8'))
            if tn.read_until('>>User password:'):
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write("\r\n")
            tn.write("\r\n")
            tn.write("enable\r\n")
            tn.write("config\r\n")
            tn.write(("display board 0/{0}\r\n".format(self.__slot)).encode('utf-8'))
            tn.write(("\r\n").encode('utf-8'))
            for i in range(15):
                tn.write("n\r\n")
            tn.read_until('display board 0/{0}'.format(self.__slot))
            result = '\n'.join(tn.read_until("  % Ambiguous command, the error locates at '^'").split('\r\n')[:-5])
            tn.write("quit\r\n")
            tn.write("quit\r\n")
            tn.write("quit\r\n")
            tn.write("y\r\n")
            tn.close()

            print('********************************')
            print(result)
            print('********************************')
            return {"result": result}

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
