import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowMac(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
        self.__port_indexes = params.get('port_indexes')
        self.port_conditions = params.get('port_conditions')

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
            tn.write(b"ip\r\n")
            tn.write(b"sm \r\n")
            tn.read_until(b' :')
            tn.write("0-{0} \r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(1)
            tn.write(b"exit\r\n")
            tn.write(b"end\r\n")
            res = tn.read_until(b'end')
            print(res)
            result = str(res).split("\\n\\r")
            result = [re.sub(r'\\t', '    ', val) for val in result if
                      re.search(r'\s{4,}|\d{2}|MAC|--+', val)]

            return dict(res=result, port_indexes=self.__port_indexes)
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
