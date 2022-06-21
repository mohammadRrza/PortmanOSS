import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class SysSnmpGetCommunity(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__snmp_name = params['snmp_name']
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
            tn.read_until(b'>>User name:')
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.read_until(b'>>User password:')
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            result = tn.read_until(b">", 0.5)
            if 'invalid' in str(result):
                return dict(result='Telnet Username or Password is wrong! Please contact with core-access department.',
                            status=500)
            if 'Reenter times' in str(result):
                return dict(result='The device is busy right now. Please try a few moments later.',
                            status=500)
            output = str(result)
            while '>' not in str(result):
                print("line 1")
                result = tn.read_until(b">", 1)
                output += str(result)
                tn.write(b"\r\n")
            print("line 2")
            tn.write(b"\r\n")
            print("line 3")
            tn.write(b"enable\r\n")
            print("line 4")
            tn.write(b"config\r\n")
            print("line 5")
            tn.write("display snmp-agent community read\r\n".encode('utf-8'))
            time.sleep(1)
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end", 1)
            print('==================================')
            if b'Community name' in result:
                dic = {}
                lst = [val for val in str(result).split('\\r\\n') if re.search(r'(:)\s\w+\s', val)]
                for i in lst:
                    a = i.strip().split(':')
                    dic[a[0]] = a[1]
                print('==================================')
                time.sleep(1)
                tn.write(b"quit\r\n")
                tn.write(b"quit\r\n")
                tn.write(b"y\r\n")
                tn.close()
                result = dic
                return dict(result=result)
            else:
                return dict(result='This SNMP Community have not been set.',
                            status=500)

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
