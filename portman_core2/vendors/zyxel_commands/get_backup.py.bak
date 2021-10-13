import telnetlib
import time
from socket import error as socket_error
from command_base import BaseCommand
import re

class GetBackUp(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_indexes = params['port_indexes']

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
            tn.read_until("Password:")
            for port_item in self.__port_indexes:
              tn.write("show config-0\r\n\r\n n".encode('utf-8'))
              time.sleep(1)
            tn.write("end\r\n")
            tn.write("exit\r\n")
            output = tn.read_until("configuration has been changed, save it? ('y' to save)")
            tn.write("y\r\n")
            tn.close()
            print '******************************************'
            print "show config"
            print '******************************************'
            return dict(results = output)
        except (EOFError, socket_error) as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
