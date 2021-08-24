import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowPort(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
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
            err1 = tn.read_until(b"#", 1)
            if "Login Failed." in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.write(b"cd service\r\n")
            tn.write("telnet Slot {0}\r\n\r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(1)
            tn.write(b"cd dsp\r\n")
            tn.write("show port status {0}\r\n\r\n".format(self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(1)
            tn.write("end\r\n".encode('utf-8'))
            result = tn.read_until(b"end")
            print(result)
            if "unreached" in str(result):
                return "The Card number maybe unavailable or does not exist."
            if "Invalid slot number!" in str(result):
                return "Card number is out of range."
            if "status:" not in str(result):
                return "Port number is out of range."
            tn.close()
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r':\s', val)]
            d = {}
            for b in result:
                i = b.split(': ', 1)
                d[i[0].strip()] = i[1].replace("\\t", "    ")
            result = d
            return result

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
