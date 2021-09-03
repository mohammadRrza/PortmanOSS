import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class SetProfileRange(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
        self.port_conditions = params.get('port_conditions')
        self.new_lineprofile = params.get('new_lineprofile')

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

    def get_dict_key(self, dict, prf):
        for key, value in dict.items():
            if str(value) == str(prf):
                return key

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST, timeout=5)
            tn.set_option_negotiation_callback(self.process_telnet_option)
            print('send login ...')
            tn.write('{0}\r\n'.format(self.__access_name).encode("utf-8"))
            err1 = tn.read_until(b"correct")
            if "incorrect" in str(err1):
                return "Access name is wrong!"
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            err2 = tn.read_until(b"Password:", 1)
            if "Invalid User Name" in str(err2):
                return "User Name is wrong."
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err3 = tn.read_until(b"OK!", 1)
            if "Invalid Password" in str(err3):
                return "Password is wrong."
            print('password sent ...')
            tn.write(b"line\r\n")
            tn.write(b"cfgport\r\n")
            tn.read_until(b'(xx-xx)')
            tn.write("0-{0} \r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(0.3)
            err4 = tn.read_until(b'(default is 1~32)', 1)
            if "not config" in str(err4):
                return f"Card number '{self.port_conditions['slot_number']}' is not configured."
            if "not exist" in str(err4):
                return f"Card number '{self.port_conditions['slot_number']}' not exist or is not available."
            if "The card ID" in str(err4):
                return f"Card number '{self.port_conditions['slot_number']}' is out of range. Please insert a number between 1-8 or 11-18"
            tn.write("{0}~{1}\r\n".format(self.port_conditions['start_port'], self.port_conditions['end_port']).encode(
                'utf-8'))
            time.sleep(0.2)
            tn.write(b"\r\n")
            tn.write(b"end")
            res = tn.read_until(b'end')
            if "The port ID is 1~32" in str(res):
                return f"Port list is out of range. Please insert a list between 1-32"
            result = [val for val in str(res).split("\\n\\r") if re.search(r'\W\s', val)]
            d = {}
            for b in result:
                i = b.split(')')
                d[i[0].replace('( ', '')] = i[1]
            result = d
            time.sleep(0.5)
            tn.write("{0}\r\n".format(self.get_dict_key(result, self.new_lineprofile)).encode('utf-8'))
            time.sleep(0.5)
            tn.read_until(b'Please input the sequence of profile:')
            tn.write("{0}\r\n".format(self.get_dict_key(result, self.new_lineprofile)).encode('utf-8'))
            time.sleep(0.5)
            err5 = tn.read_until(b"ok!", 3)
            if "ok!" not in str(err5):
                return "Profile number is out of range."

            tn.write(b"cp\r\n")
            tn.read_until(b'(xx-xx)')
            tn.write("0-{0} \r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.read_until(b'(default is 1~32)')
            tn.write("{0}~{1}\r\n".format(self.port_conditions['start_port'], self.port_conditions['end_port']).encode(
                'utf-8'))
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.read_until(b'OK.')
            tn.write(b"op\r\n")
            tn.read_until(b'(xx-xx)')
            tn.write("0-{0} \r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.read_until(b'(default is 1~32)')
            tn.write("{0}~{1}\r\n".format(self.port_conditions['start_port'], self.port_conditions['end_port']).encode(
                'utf-8'))
            time.sleep(0.5)
            tn.write(b"\r\n")
            tn.read_until(b'finished.')
            tn.write(b"finish")
            res = tn.read_until(b'finish')
            tn.write(b"exit\r\n")
            tn.close()

            return "Profiles range set successfully"
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno)))
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
