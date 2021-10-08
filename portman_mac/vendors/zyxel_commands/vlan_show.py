import telnetlib
import time
from .command_base import BaseCommand
import re

class VlanShow(BaseCommand):
    def __init__(self, params):
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
            tn = telnetlib.Telnet(self.__HOST,23,20)
            time.sleep(1)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if self.__telnet_password:
                tn.read_until("Password: ")
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.write(("vlan show\r\n").encode('utf-8'))
            time.sleep(1)
            tn.write("end\r\n")
            result = tn.read_until('end')
            results = result.split('\n')
            vlans = {}
            for line in results[5:len(results)-2]:
                items = line.split()
                vlans[items[0]] = items[-1]
            tn.write("exit\r\n")
            tn.write("y\r\n")
            tn.close()
            return vlans
        except Exception as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
            else:
                return None
