import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class PortPvcShow(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.port_conditions = params.get('port_conditions')
        self.device_ip = params.get('device_ip')
        self.__port_indexes = params.get('port_indexes')

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

    retry = 1
    
    def run_command(self):
        try:
            print('run_command')
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            for port_item in self.__port_indexes:
                tn.write("port pvc show {0}-{1}\r\n\r\n".format(port_item['slot_number'], port_item['port_number']).encode('utf-8'))
            time.sleep(0.5)
            tn.write(b"end\r\n")
            result = tn.read_until(b'end')
            if "example:" in str(result):
                return 'slot number or port number is out of range.'
                # result = str(result).split("\\r\\n")
                # result = [val for val in result if re.search(r'example|between', val)]
                # return result
            if "inactive" in str(result):
                return f"slot {self.__port_indexes[0]['slot_number']} is inactive."
                # result = str(result).split("\\r\\n")
                # result = [val for val in result if re.search(r'inactive', val)]
                # return result
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('******************************************')
            print(("port enable {0}".format(self.port_conditions)))
            print('******************************************')
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r'\s{3,}|--{3,}', val)]
            result = result[2:]
            result = [re.sub(r'\s{3,}', ',', line).split(",") for line in result]
            res = []
            for line in result:
                res.append(dict(pvc=line[0], type=line[1], mux=line[2], pvid=line[3], pri=line[4], mvlan=line[5],
                                profile=line[6]))
            return res
            # return dict(res1 = result[5].split('-')[2].split()[0] ,res2 = result[5].split('-')[2].split()[3],result = '')
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print((str(exc_tb.tb_lineno)))
            print(e)
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            self.retry += 1
            if self.retry < 3:
                return self.run_command()
