import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class ShowShelf(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
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
            err1 = tn.read_until(b"correct")
            if "incorrect" in str(err1):
                return "Access name is wrong!"
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            err2 = tn.read_until(b"Password:", 1)
            if "Invalid User Name" in str(err2):
                return "User Name is wrong."
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err3 = tn.read_until(b"OK!", 1)
            if "Invalid Password" in str(err3):
                return "Password is wrong."
            print('password sent ...')
            tn.write("sc\r\n".encode('utf-8'))
            time.sleep(1)
            tn.write("end\r\n".encode('utf-8'))
            res = tn.read_until(b'end')
            tn.write(b"exit\r\n")
            tn.close()
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                print("self.device_ip == '127.0.0.1'")
                return dict(result=re.sub(r'-{2,}\w*\s\w*\s\w*\s\w*\s\w*\s\w*.\w\s\w*\s\w*\-{2,}\s\W.\d.*', '', res.decode('utf-8')), status=200)
            result = str(res).split("\\n\\r")
            result = [val for val in result if re.search(r'\s{4,}|SHELF|Polling|Current|--+', val)]
            return dict(result=result, status=200)

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
