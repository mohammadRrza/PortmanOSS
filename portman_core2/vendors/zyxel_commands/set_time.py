import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class SetTime(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_indexes = params.get('port_indexes')
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
                tn.write(b"sys timeserver set  ntp 172.22.10.110 utc+0330\r\n\r\n")
                tn.write(b"sys timeserver sync\r\n\r\n")
                tn.write(b"co sa\r\n\r\n")
                time.sleep(1)
            tn.write(b"end\r\n")
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('******************************************')
            print("")
            print('******************************************')
            return dict(result="Time set successfully", status=500)
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
