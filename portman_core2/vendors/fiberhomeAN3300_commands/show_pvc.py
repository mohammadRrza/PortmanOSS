import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowPVC(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__lineprofile = params.get('new_lineprofile')
        self.__access_name = params.get('access_name', 'an3300')
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
            tn.write("show dsl-profile {0}\r\n".format(self.__lineprofile).encode('utf-8'))
            time.sleep(0.5)
            # result1 = tn.read_until(b"--Press any key to continue Ctrl+c to stop--")
            tn.write(b"\r\n")
            time.sleep(0.5)
            tn.write(b"\r\n")
            time.sleep(0.5)
            tn.write(b"\r\n")
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.write(b"end")
            result = tn.read_until(b"end")
            tn.close()
            result = str(result).split("\\r\\n")
            result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+H', '', val) for val in result if re.search(r'pvc\d|vpi|vci', val)]
            res = []
            for inx, val in enumerate(result):
                if "pvc" in val:
                    temp = {}
                    temp[val.split(':')[0].strip()] = {}
                    temp[val.split(":")[0].strip()]['vpi'] = result[inx + 1].split(":")[1]
                    temp[val.split(":")[0].strip()]['vci'] = result[inx + 2].split(":")[1]
                    res.append(temp)
            return res

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
