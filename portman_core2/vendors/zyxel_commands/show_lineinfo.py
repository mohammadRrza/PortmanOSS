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
        self.__port_indexes = params.get('port_indexes')

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
                tn.write("show lineinfo {0}-{1}\r\n\r\n".format(port_item['slot_number'], port_item['port_number']).encode('utf-8'))
                time.sleep(1)
            tn.read_until(b"Communications Corp.")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('*******************************************')
            print(("show lineinfo {0}".format(result)))
            print('*******************************************')
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r':\s', val)]
            d = {}
            for b in result:
                i = b.split(': ')
                d[i[0].strip()] = i[1]
            result = d
            return result
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
