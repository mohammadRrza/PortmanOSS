import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowAllVLANs(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
        self.__port_indexes = params.get('port_indexes')
        self.port_conditions = params.get('port_conditions')
        self.__vlan_name = params.get('vlan_name')
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

    def process_telnet_option(self, tsocket, command, option):
        from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS, LINEMODE, ECHO
        tsocket.sendall(IAC + WONT + LINEMODE)

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST, timeout=5)
            tn.set_option_negotiation_callback(self.process_telnet_option)
            print('send login ...')
            tn.write('{0}\r\n'.format(self.__access_name).encode("utf-8"))
            data = tn.read_until(b'User Name:')
            print('here')
            print('==>', data)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            print('user sent ...')
            data = tn.read_until(b'Password:')
            print('==>', data)
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            print('password sent ...')
            time.sleep(0.5)
            tn.write(b"ip\r\n")
            tn.write(b"sv\r\n")
            temp = tn.read_until(b'IP')
            if b"NO ip uplink" in temp:
                return str(temp)
            tn.read_until(b'vlan(1,2):')
            tn.write(b"2\r\n")
            time.sleep(0.5)
            tn.read_until(b'(xx,xx~xx)     :')
            tn.write(b"\r\n")
            time.sleep(1)
            tn.write(b"\r\n")
            tn.write(b"end")
            res = tn.read_until(b'end')
            tn.close()
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return res.decode('utf-8')
            res = str(res).replace('\\r', '')
            result = str(res).split("\\n")
            result = [val for val in result if re.search(r'--{4,}|[:]', val)]
            # d = {}
            # for b in result:
            #     i = b.split(' :')
            #     d[i[0].strip()] = i[1].replace("\\r", "").strip()
            # result = d
            return result
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
            if self.retry < 3:
                return self.run_command()
