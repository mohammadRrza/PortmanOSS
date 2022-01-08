import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ResetSIPConfiguration(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_indexes = params.get('port_indexes')
        self.device_ip = params.get('device_ip')
        self.Gateway = params.get('gateway')
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
            if tn.read_until(b'>>User name:'):
                print(self.__telnet_username)
                tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if tn.read_until(b'>>User password:'):
                print(self.__telnet_password)
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"eenable\r\n")
            print('==================================================================================')
            print('eenable')
            tn.write(b"enable\r\n")
            print('enable')
            tn.write(b"config\r\n")
            print('config')
            tn.write(b"interface sip 0\r\n")
            print('interface sip 0')
            tn.write(b"reset\r\n")
            print('reset')
            if tn.read_until(b'Are you sure to reset the SIP interface?'):
                print('Are you sure to reset the SIP interface?')
                tn.write(b"y\r\n")
            tn.write(b"end\r\n")
            print('==================================================================================')
            result = tn.read_until(b'end')
            tn.write(b"quit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            return dict(result=str(result), port_indexes=self.__port_indexes)
        except (EOFError, socket_error) as e:
            print('============socket_error==========')
            print(e)
            print('============socket_error==========')
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            print('============Exception==========')
            print(e)
            print('============Exception==========')
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
