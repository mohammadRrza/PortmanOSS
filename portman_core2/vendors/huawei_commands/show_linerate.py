import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class ShowLineRate(BaseCommand):
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

    retry = 1
    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            if tn.read_until(b'>>User name:'):
                tn.write((self.__telnet_username + "\n").encode('utf-8'))
            if tn.read_until(b'>>User password:'):
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write(b"enable\r\n")
            tn.write(b"config\r\n")
            for port_item in self.__port_indexes:
                tn.write(("interface adsl 0/{0}\r\n".format(port_item['slot_number'])).encode('utf-8'))
                tn.write(("display line operation {0}\r\n".format(port_item['port_number'])).encode('utf-8'))
                tn.read_until(("display line operation {0}\r\n".format(port_item['port_number'])).encode('utf-8'))
                tn.write(b"y\r\n")
                #tn.write(("\r\n").encode('utf-8'))
                tn.write(b"quit\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            print(result)
            #result = '\n'.join(eval(repr(tn.read_until('Upstream total output power(dBm)')).replace(r"---- More ( Press 'Q' to break ) ----\x1b[37D                                     \x1b[37D","")).split("\r\n")[:-1])
            # tn.write("quit\r\n")
            # tn.write("quit\r\n")
            # tn.write("y\r\n")
            # tn.close()
            print('*******************************************')
            print(("show linerate {0}".format(result)))
            print('*******************************************')
            return {"result": str(result)}
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno)))
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
