import os
import sys
import telnetlib
from socket import error as socket_error

from .command_base import BaseCommand
import re


class AnnexmShow(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.device_ip = params.get('device_ip')
        self.port_conditions = params.get('port_conditions')
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
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b"Communications Corp.", 10)
            if "Password:" in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)

            tn.write("adsl annexm show {0}\r\n".format(self.port_conditions['port_number']).encode('utf8'))
            tn.write(b"end")
            result = tn.read_until(b"end")
            tn.write(b"exit\r\n")
            tn.close()
            if "<port>" in str(result):
                return dict(result=f"Port number '{self.port_conditions['port_number']}' is out of range.", status=500)
            if self.request_from_ui:
                return dict(result=result.decode('utf-8'), status=200)
            result = str(result).split('\\r\\n')
            result = [item for item in result if re.search(r"\s+\d+\s+|\A\w+\s+", item)]
            return dict(result=result, status=200)


        except (EOFError, socket_error) as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno) + '//1'))
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno) + '//2'))
            print(e)
            print(e)
            return str(e)