import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class ShowLineInfo(BaseCommand):
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
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)
            tn.write("show lineinfo {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'], self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if "example:" in str(result):
                result = str(result).split("\\r\\n")
                result = [val for val in result if re.search(r'example|between', val)]
                return dict(result=result, status=500)
            if "inactive" in str(result):
                result = str(result).split("\\r\\n")
                result = [val for val in result if re.search(r'inactive', val)]
                return dict(result=result, status=500)
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('*******************************************')
            print(("show lineinfo {0}".format(result)))
            print('*******************************************')
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=result.decode('utf-8'), status=200)
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r':\s', val)]
            d = {}
            for b in result:
                i = b.split(': ')
                d[i[0].strip()] = i[1]
            result = d
            return dict(result=result, status=200)
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno)))
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
