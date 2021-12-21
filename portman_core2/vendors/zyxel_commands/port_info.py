import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class PortInfo(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
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
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.write("port show {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'],
                                                        self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b'end')
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=result.decode('utf-8'), status=200)
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r'\s{2,}|--{3,}', val)]
            for inx, val in enumerate(result):
                if "Press" in val:
                    result.pop(inx)
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('******************************************')
            print(("port enable {0}".format(self.port_conditions)))
            print('******************************************')
            return result
            return dict(result=result)
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
