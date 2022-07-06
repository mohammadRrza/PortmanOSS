import telnetlib
import time
from .command_base import BaseCommand
import re


class VlanShow(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.device_ip = params.get('device_ip')
        self.request_from_ui = params.get('request_from_ui')

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
            result = ''
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)
            tn.read_until(b'#')
            tn.write(b"vlan show\r\nn")
            output = tn.read_until(b'#', 1)
            result += output.decode('utf-8')
            tn.write(b"show vlan\r\nn")
            output = tn.read_until(b'#', 1)
            result += output.decode('utf-8')
            if self.request_from_ui:
                return dict(result=result, status=200)
            result = str(result).split('\\r\\n')
            result = [val for val in result if re.search(r'\s{3,}|--{4,}|vid', val)]
            for inx, line in enumerate(result):
                if "Press any key" in line:
                    del result[inx:inx + 3]
            vlans = {}
            for line in result[2:]:
                if "vid" in line:
                    break
                temp = line.split()
                vlans[temp[0]] = temp[-1]
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('********************************')
            print(result)
            print('********************************')
            return dict(vlans=vlans, result=result, status=200)
        except Exception as e:
            print('***************Exception*****************')
            print(e)
            print('***************Exception*****************')
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
