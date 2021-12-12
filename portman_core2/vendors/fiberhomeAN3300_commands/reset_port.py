import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ResetPort(BaseCommand):
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
            tn.write(b"cd device\r\n")
            tn.write("set xdsl port {0}:{1} disable\r\n\r\nset xdsl port {0}:{1} enable\r\n".format(
                self.port_conditions['slot_number'],
                self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            tn.close()
            if "invalid port list." in str(result):
                return "The port list is out of range!"
            else:
                tn.close()
                return dict(result="Port restarted successfully.", status=200)
            # return str(result)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
