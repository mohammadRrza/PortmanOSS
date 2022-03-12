import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowProfileByPort(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
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
            tn.read_until(b'>>User name:')
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.read_until(b'>>User password:')
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            result = tn.read_until(b">", 0.5)
            output = str(result)
            while '>' not in str(result):
                result = tn.read_until(b">", 1)
                output += str(result)
                tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"enable\r\n")
            tn.write(b"config\r\n")
            tn.read_until(b"(config)#")
            tn.write(("interface adsl 0/{0}\r\n".format(self.__port_indexes['slot_number'])).encode('utf-8'))
            result = tn.read_until(b"#")
            if "Parameter error, the error locates at" in str(result):
                return dict(result="Card number is out of range.", status=500)
            if "Failure:" in str(result):
                tn.write(("interface vdsl 0/{0}\r\n".format(self.__port_indexes['slot_number'])).encode('utf-8'))
                result = tn.read_until(b"#")
                if "Parameter error, the error locates at" in str(result):
                    return dict(result="Card number is out of range.", status=500)
            print('++++++++++++++')
            tn.write(b'\r\n')
            tn.read_until(b"#")
            tn.write(("display parameter {0}\r\n".format(self.__port_indexes['port_number'])).encode('utf-8'))
            result = tn.read_until(b"#", 0.1)
            output = str(result)
            while '#' not in str(result):
                tn.write(b"\r\n")
                result = tn.read_until(b"#", 0.1)
                output += str(result.decode('utf-8'))
            result = output.split("\r\n")
            profile_index = None
            profile_name = None
            for item in result:
                if "Line-profile" in item or "Profile index" in item:
                    profile_index = item.split(":")[1].split()[0].strip()
                    profile_name = item.split(":")[2].strip()
            tn.write(b"quit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('*******************************************')
            print(result)
            print('*******************************************')
            return dict(result=profile_name, profile_name=profile_name, profile_index=profile_index)
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
