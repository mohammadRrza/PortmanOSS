import telnetlib
import time
from socket import error as socket_error
from command_base import BaseCommand
import re

class ShowMac(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None

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
        results = []
        try:
            tn = telnetlib.Telnet(self.__HOST)
            if tn.read_until('>>User name:'):
                tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if tn.read_until('>>User password:'):
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write("\r\n")
            tn.write("\r\n")
            tn.write("enable\r\n")
            tn.write("config\r\n")
            tn.write(("display mac-address all\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n").encode('utf-8'))
            for item in range(7):
                time.sleep(1)
                tn.write("n\r\n")
                tn.write("next\r\n")
                result = tn.read_until("next")
                if 'next' in result:
                    break
            print result
            com =re.compile(r'(?P<mac>\w{4}-\w{4}-\w{4})\s+\S+\s+\d{1}(\s)?/(?P<slot_number>\d+)(\s/(?P<port_number>\d+)\s+[\d+|\-]+\s+[\d+|\-]+)?\s+(?P<vlan_id>(\d+|\w+))')
            results = [m.groupdict() for m in com.finditer(result)]
            tn.write("quit\r\n")
            tn.write("y\r\n")
            tn.close()
            print '***********************'
            print results
            print '***********************'
            return {'result': results}
        except (EOFError,socket_error) as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception,e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
