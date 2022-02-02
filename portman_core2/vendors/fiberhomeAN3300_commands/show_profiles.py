import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowProfiles(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__vlan_name = params.get('vlan_name')
        self.__access_name = params.get('access_name', 'an3300')
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

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write(b"end\r\n")
            err1 = tn.read_until(b"end")
            if "Login Failed." in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.read_until(b"User>")
            tn.write(b'admin\r\n')
            tn.read_until(b"Password:")
            tn.write('{0}\r\n'.format(self.__access_name).encode('utf-8'))
            time.sleep(0.5)
            err1 = tn.read_until(b"#", 1)
            if "Bad Password..." in str(err1):
                return "DSLAM Password is wrong!"
            tn.write(b"cd profile\r\n")
            tn.read_until(b"profile#", 0.1)
            tn.write(b"show all dsl-profile-name\r\n")
            result = tn.read_until(b"profile#", 0.5)
            output = str(result)
            while 'profile#' not in str(result):
                result = tn.read_until(b"profile#", 0.5)
                output += str(result)
                tn.write(b"\r\n")
            res = result
            result = output
            tn.close()
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=re.sub(r'-{2,}\w*\s\w*\s\w*\s\w*\s\w*\s\w*.\w\s\w*\s\w*\-{2,}\s\W.\d.*', '', res.decode('utf-8')), status=200)
            result = str(result).split("\\r\\n")
            # return dict(result=result, status=200)
            result = [re.sub(r"\s+--P[a-zA-Z '+\\1-9[;-]+H", "", val) for val in result if re.search(r'\s{4,}', val)][1:]
            temp_res = []
            for i in result:
                temp_res += i.split()
            return dict(result=temp_res, status=200)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
