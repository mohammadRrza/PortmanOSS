import csv
import telnetlib
import re
import time
from .command_base import BaseCommand
import sys, os

class AddToVlan(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
        self.__vlan_name = params.get('vlan_name')
        self.port_conditions = params.get('port_indexes')
        self.reseller = params.get('reseller').split('-')[1]
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

    def __clear_port_name(self, port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern, port_name, re.M | re.DOTALL)
        return st.group()

    def process_telnet_option(self, tsocket, command, option):
        from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS, LINEMODE, ECHO
        tsocket.sendall(IAC + WONT + LINEMODE)

    def run_command(self):
        try:
            WANE2W_par = None
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
            tn.write(b"sc\r\n")
            tn.write(b"end\r\n")
            WANE2W_obj = tn.read_until(b'end')
            for item in str(WANE2W_obj).split('\\n\\r'):
                if 'WANE2W' in item:
                    WANE2W_par = item.split()[1]

            tn.write("ip\r\n".encode('utf-8'))
            tn.write("dfv\r\n".encode('utf-8'))
            tn.write("pte\r\n".encode('utf-8'))
            tn.write("\r\n".encode('utf-8'))
            tn.write("0-{0}-{1}\r\n".format(self.port_conditions[0]['slot_number'],
                                            self.port_conditions[0]['port_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write("N\r\n".encode('utf-8'))
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if "Untag port to be deleted is not in vlan pte!" in str(result):
                return f"Card {self.port_conditions[0]['slot_number']} and Port {self.port_conditions[0]['port_number']} is not in vlan pte."
            tn.write("addtovlan\r\n".encode('utf-8'))
            time.sleep(0.2)
            tn.write("{0}\r\n".format(self.__vlan_name).encode('utf-8'))
            time.sleep(0.2)
            tn.write("0-{0}-1\r\n".format(WANE2W_par).encode('utf-8'))
            time.sleep(0.2)
            tn.write("0-{0}-{1}\r\n".format(self.port_conditions[0]['slot_number'],
                                            self.port_conditions[0]['port_number']).encode('utf-8'))
            time.sleep(0.2)
            tn.write("N\r\n".encode('utf-8'))
            tn.write("endn\r\n".encode('utf-8'))
            result = tn.read_until(b'endn')
            print('===================================')
            print(result)
            print('===================================')
            tn.write(b"exit\r\n\r\n")
            tn.close()
            if 'Continue to add port' in str(result):
                return 'port {0}-{1} added to vlan {2}'.format(self.port_conditions[0]['slot_number'],
                                                               self.port_conditions[0]['port_number'], self.__vlan_name)

        except Exception as ex:
             exc_type, exc_obj, exc_tb = sys.exc_info()
             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
             return "Error is: {0} in line {1}".format(format(ex), str(exc_tb.tb_lineno))
