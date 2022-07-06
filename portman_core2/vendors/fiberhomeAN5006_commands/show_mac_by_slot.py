import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class ShowMacBySlot(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
        self.device_ip = params.get('device_ip')
        self.request_from_ui = params.get('request_from_ui')

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
            tn.write("show linecard fdb interface {0}\r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            err2 = tn.read_until(b"device#", 0.2)
            if "there is no mac" in str(err2):
                return dict(
                    result=f"There is no mac address learned by slot {self.port_conditions['slot_number']} port {self.port_conditions['port_number']}",
                    status=500)
            if "invalid" in str(err2):
                return dict(result=f"Card number {self.port_conditions['slot_number']} is out of range.", status=500)
            if "Unknown command." in str(err2):
                tn.write(
                    "show mac-address interface {0}\r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
                time.sleep(1.5)
                tn.write(b"\r\n")
                tn.write(b"\r\n")
                tn.write(b"end\r\n")
                result = tn.read_until(b"end")
                tn.write(b"\r\n")
                if "invalid interface" in str(result):
                    str_res = ["There is one of the following problems:",
                               "This card is not configured or not available", "Card number is out of range."]
                    return dict(result=str_res, status=500)
                if "total: 0." in str(result):
                    return dict(result=f"No MAC address is assigned to slot '{self.port_conditions['slot_number']}'",
                                status=500)
                tn.close()
                if self.request_from_ui:
                    return dict(result=result.decode('utf-8'), status=200)
                result = str(result).split("\\r\\n")
                result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+J', '', val) for val in result if
                          re.search(r'\s{3,}|--{4,}|:|learning', val)]
                return dict(result=result, status=200)
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if "invalid interface" in str(result):
                str_res = ["There is one of the following problems:",
                           "This card is not configured or not available", "Card number is out of range."]
                return dict(result=str_res, status=500)
            if "total: 0." in str(result):
                return dict(result=f"No MAC address is assigned to port '{self.port_conditions['port_number']}'",
                            status=500)
            tn.close()
            result = str(result).split("\\r\\n")
            if self.request_from_ui:
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
