import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ACLMacCountShow(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_name = None
        self.__port_indexes = params.get('port_conditions')
        self.device_ip = params.get('device_ip')

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
                tn.write((self.__telnet_username + "\n").encode('utf-8'))
            if tn.read_until(b'>>User password:'):
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write(b"end")
            err = tn.read_until(b'end')
            if 'invalid' in str(err):
                return dict(result='Telnet Username or Password is wrong! Please contact with core-access department.',
                            status=500)
            if 'Reenter times' in str(err):
                return dict(result='The device is busy right now. Please try a few moments later.',
                            status=500)
            tn.write(b"\r\n")
            tn.write(b"enable\r\n")
            tn.write(b"config\r\n")
            tn.read_until(b"(config)#")
            tn.write("display mac-address max-mac-count adsl 0/{0}/{1}\r\n".format(self.__port_indexes['slot_number'], self.__port_indexes['port_number']).encode('utf-8'))
            tn.write(b"\r\n")
            result = tn.read_until(b"(config)#")
            if "Parameter error" in str(result):
                return dict(result="Card number or Port number is wrong.", status=500)
            if "Failure:" in str(result):
                return dict(result="There is not any MAC address record", status=500)
            output = str(result)
            while '(config)#' not in str(result):
                tn.write(b"\r\n")
                result = tn.read_until(b"(config)#", 0.1)
                output += str(result.decode('utf-8'))


            #result = [val for val in result if re.search(r'^(?![\s\S])|:|Total', val)]
            tn.write(b"quit\r\n")
            tn.write(b"quit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('**************************************')
            print(result)
            print('**************************************')
            result = output.split("\\r\\n")
            result = [item for item in result if re.search(r"-{4,}|:\s\d+|\s{2,}\w+\s{2,}", item)]
            return dict(result=result, status=200)
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
