import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ClosePort(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
        self.__port_indexes = params.get('port_indexes')
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
            time.sleep(0.5)
            err1 = tn.read_very_eager()
            if "incorrect" in str(err1):
                return dict(result="Access name is wrong!", status=500)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            time.sleep(0.5)
            err2 = tn.read_very_eager()
            if "Invalid User Name" in str(err2):
                return dict(result="User Name is wrong.", status=500)
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(0.5)
            err3 = tn.read_very_eager()
            if "Invalid Password" in str(err3):
                return dict(result="Password is wrong.", status=500)
            print('password sent ...')
            tn.write(b"line\r\n")
            tn.write(b"cp\r\n")
            time.sleep(0.5)
            tn.read_very_eager()
            tn.write("0-{0} \r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(0.5)
            err4 = tn.read_very_eager()
            if "not config" in str(err4):
                tn.close()
                return dict(result=f"Card number '{self.port_conditions['slot_number']}' is not configured.", status=500)
            if "not exist" in str(err4):
                tn.close()
                return dict(result=f"Card number '{self.port_conditions['slot_number']}' not exist or is not available.", status=500)
            if "The card ID" in str(err4):
                tn.close()
                return dict(result=f"Card number '{self.port_conditions['slot_number']}' is out of range. Please insert a number between 1-8 or 11-18", status=500)
            tn.write("{0} \r\n".format(self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.write(b"finish")
            time.sleep(0.5)
            res = tn.read_very_eager()
            if "timeout!!" in str(res):
                tn.close()
                return dict(result="Timeout! Please try again.", status=500)
            if "The port is" in str(res):
                tn.close()
                return dict(result=f"Port number '{self.port_conditions['port_number']}' is out of range. Please insert a number between 1-32", status=500)
            if self.request_from_ui:
                tn.close()
                return dict(result=res.decode('utf-8'), status=200)
            result = str(res).split("\\n\\r")
            result = [val for val in result if 'The port' in val or "OK" in val]
            tn.write(b"exit\r\n")
            tn.close()

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
