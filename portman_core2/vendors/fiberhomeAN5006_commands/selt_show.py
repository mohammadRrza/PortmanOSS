import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re
import sys, os


class ShowSelt(BaseCommand):
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
            tn.write("telnet Slot {0}\r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(2)
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            err2 = tn.read_until(b"end")
            if "unreached" in str(err2):
                return f"The Card '{self.port_conditions['slot_number']}' maybe unavailable or does not exist."
            if "Invalid slot number!" in str(err2):
                return f"Card '{self.port_conditions['slot_number']}' is out of range."
            tn.write(b"ddd\r\n")
            tn.write(b"set global io current\r\n")
            time.sleep(0.1)
            tn.write(b"exit\r\n")
            tn.write(b"cd dsp\r\n")

            tn.write("selt start {0}\r\n".format(self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.2)
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            err3 = tn.read_until(b"end")
            if "Invalid port No." in str(err3):
                return f"Invalid port number '{self.port_conditions['port_number']}'"
            tn.write(b"exit\r\n")
            tn.write(b"exit\r\n")
            tn.write(b"exit\r\n")
            tn.write(b"\r\n")
            tn.write(b"cd ..\r\n")
            tn.write(b"save\r\n")
            time.sleep(1)
            tn.write(b"cd service\r\n")
            tn.write("telnet Slot {0}\r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.write(b"ddd\r\n")
            time.sleep(0.2)

            tn.write(b"set global io current\r\n")
            time.sleep(0.1)

            tn.write(b"exit\r\n")
            tn.write(b"\r\n")
            tn.write(b"cd dsp\r\n")
            time.sleep(0.2)
            tn.write(b"\r\n")

            tn.write("selt get {0}\r\n".format(self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.2)
            tn.write(b"\r\n")

            tn.write("end\r\n".encode('utf-8'))
            result = tn.read_until(b"end", 1)
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r'=|Loop', val)]
            tn.close()

            return result

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(exc_tb.tb_lineno)
