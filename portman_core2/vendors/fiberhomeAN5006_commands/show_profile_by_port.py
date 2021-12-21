import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowProfileByPort(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
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
            err1 = tn.read_until(b"#", 1)
            if "Login Failed." in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.write(b"cd dsl\r\n")
            tn.write("show pvc profile attach interface {0}/{1}\r\n".format(self.port_conditions['slot_number'],
                                                                            self.port_conditions['port_number']).encode(
                'utf-8'))
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return result.decode('utf-8')
            if "SlotNoPortConvertObjIndex" in str(result):
                return "The Card number maybe unavailable or does not exist."
            elif "ifStr" in str(result):
                return "Card number or Port number is out of range."
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r'\s{3,}', val)]
            profile_id = f"id: {result[1].split()[2]}"
            print(profile_id)

            tn.write(b"cd qos\r\n")
            time.sleep(0.1)
            tn.write(b"show rate-limit profile all\r\n")
            time.sleep(1)
            tn.write(b"\r\n")
            time.sleep(0.1)
            tn.write(b"\r\n")
            time.sleep(0.1)
            tn.write(b"\r\n")
            time.sleep(0.1)
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end", 1)
            tn.close()
            result = str(result).split("\\r\\n")
            result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+J', '', val) for val in result if
                      re.search(r':\s', val)]
            for inx, val in enumerate(result):
                if profile_id in val:
                    prf_name = result[inx + 1].split(":")[1].strip()
                    result = f"Profile set to card '{self.port_conditions['slot_number']}' and port '{self.port_conditions['port_number']}' is: '{prf_name}'"
                    return dict(result=result, status=200)
            else:
                return "Profile not found."

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(exc_tb.tb_lineno)
