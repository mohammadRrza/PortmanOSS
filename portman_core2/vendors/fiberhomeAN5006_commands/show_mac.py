import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowMac(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
        self.device_ip = params.get('device_ip')
        self.cards_status = params.get('cards_status')

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
            err1 = tn.read_until(b"#", 0.2)
            if "Login Failed." in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.",
                            status=500)
            tn.write(b"cd device\r\n")
            tn.read_until(b"device#")
            output = ''
            for item in self.cards_status[:-1]:
                tn.write("show linecard fdb interface {0}\r\n".format(item['Card']).encode('utf-8'))
                time.sleep(1.5)
                tn.write(b"\r\n")
                tn.write(b"\r\n")
                err2 = str(tn.read_until(b"device#", 0.6))
                if "Unknown command." in err2:
                    break
                output += err2
            for item in self.cards_status[:-1]:
                tn.write(b"\r\n")
                tn.write(b"\r\n")
                tn.write(
                    "show mac-address interface {0}\r\n".format(item['Card']).encode('utf-8'))
                time.sleep(1.5)
                tn.write(b"\r\n")
                tn.write(b"\r\n")
                err3 = str(tn.read_until(b"device##", 0.6))
                if "Unknown command." in err3:
                    break
                output += err3

            result = output.split('\\r\\n')
            result = [re.sub(r"\s+--P[a-zA-Z +\\1-9[;-]+J|\s+--P[a-zA-Z +'b'\\1-9[;-]+J", '', val) for val in result if
                      re.search(r'\s{3,}|--{4,}|:|learning', val)]
            tn.close()
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                str_join = "\r\n"
                str_join = str_join.join(result)
                return dict(result=str_join, status=200)
            return dict(result=result, status=200)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return "error"
