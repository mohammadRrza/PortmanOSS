import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowFastProfiles(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
        self.device_ip = params.get('device_ip')
        self.request_from_ui = params.get('request_from_ui')

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
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b"#", 1)
            if "Login Failed." in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)
            tn.write(b"cd dsl\r\n")
            tn.read_until(b'dsl#')
            time.sleep(0.1)
            tn.write(b"show adsl line-profile\r\n")
            result = tn.read_until(b"dsl#", 0.5)
            output = str(result)
            while 'dsl#' not in str(result):
                result = tn.read_until(b"dsl#", 1)
                output += str(result)
                tn.write(b"\r\n")
            tn.close()


            result = str(output).split("\\r\\n")

            result = [item.split()[2] for item in result if
                      re.search("\s\d+\d+\s", item)]
            if self.request_from_ui:
                str_join = "\r\n"
                str_join = str_join.join(result)
                return dict(result=str_join, status=200)
            return dict(result=result, status=200)

        except (EOFError, socket_error) as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(str(exc_tb.tb_lineno))
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(str(exc_tb.tb_lineno))
            return str(e)
