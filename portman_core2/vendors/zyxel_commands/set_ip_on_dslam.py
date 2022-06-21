import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class SetIpOnDslams(BaseCommand):
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
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.",
                            status=500)

            tn.write(b"sys client enable 1\r\n\r\n")
            tn.write(b"sys client set 1 109.125.191.1 109.125.191.254 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 2\r\n\r\n")
            tn.write(b"sys client set 2 5.202.129.170 5.202.129.170 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 3\r\n\r\n")
            tn.write(b"sys client set 3 172.28.237.97 172.28.237.110 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 4\r\n\r\n")
            tn.write(b"sys client set 4 5.202.112.234 5.202.112.234 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 5\r\n\r\n")
            tn.write(b"sys client set 5 5.202.129.160 5.202.129.160 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 6\r\n\r\n")
            tn.write(b"sys client set 6 172.28.238.0 172.28.238.255 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 7\r\n\r\n")
            tn.write(b"sys client set 7 172.28.244.48 172.28.244.63 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 8\r\n\r\n")
            tn.write(b"sys client set 8 172.28.246.130 172.28.246.132 telnet ftp web icmp ssh snmp https\r\n\r\n")
            tn.write(b"sys client enable 9\r\n\r\n")
            tn.write(b"sys client set 9 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 10\r\n\r\n")
            tn.write(b"sys client set 10 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 11\r\n\r\n")
            tn.write(b"sys client set 11 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 12\r\n\r\n")
            tn.write(b"sys client set 12 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 13\r\n\r\n")
            tn.write(b"sys client set 13 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 14\r\n\r\n")
            tn.write(b"sys client set 14 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 15\r\n\r\n")
            tn.write(b"sys client set 15 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"sys client disable 16\r\n\r\n")
            tn.write(b"sys client set 16 0.0.0.0 0.0.0.0\r\n\r\n")
            tn.write(b"config save\r\n\r\n")
            tn.write(b"sys client show\r\n\r\n")
            time.sleep(0.5)
            tn.write(b"end\r\n\r\n")
            result = tn.read_until(b"end")
            return dict(result=result.decode('utf-8'), status=200)
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
