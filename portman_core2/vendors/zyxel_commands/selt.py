import os
import telnetlib
import sys
import time
from .command_base import BaseCommand
from socket import error as socket_error
import re


class Selt(BaseCommand):
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

    def __clear_port_name(self,port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern,port_name,re.M|re.DOTALL)
        return st.group()

    retry = 1

    def run_command(self):
        output = ""
        results = []
        try:
            prompt = 'command'
            c_n = 1
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            # tn.write("diagnostic selt test {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'], self.port_conditions['port_number']).encode(
            #         'utf-8'))
            # time.sleep(40)
            # tn.write("diagnostic selt show {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'], self.port_conditions['port_number']).encode(
            #         'utf-8'))
            # output = tn.read_until(b"kFt)")
            # if "FAIL_FIND_REFLECTION" in str(output):
            #     return "Port is down or not available."
            # if "INPROGRESS" in str(output):
            #     return "Selt command is not available."
            tn.write("diagnostic selt test {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'], self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(1)
            tn.write((str(prompt)+str(c_n)+"\r\n").encode('utf-8'))
            time.sleep(0.2)
            err2 = tn.read_until((str(prompt)+str(c_n)).encode('utf-8'))
            if "example:" in str(err2):
                result = str(err2).split("\\r\\n")
                result = [val for val in result if re.search(r'example|between', val)]
                return dict(result=result, status=500)
            if "inactive" in str(err2):
                result = str(err2).split("\\r\\n")
                result = [val for val in result if re.search(r'inactive', val)]
                return dict(result=result, status=500)
            c_n += 1
            tn.write("diagnostic selt show {0}-{1}\n".format(self.port_conditions['slot_number'], self.port_conditions['port_number']).encode('utf-8'))
            tn.write((str(prompt)+str(c_n)+"\r\n").encode('utf-8'))
            output = tn.read_until((str(prompt)+str(c_n)).encode('utf-8'))
            while 'INPROGRESS' in str(output):
                print('----------------------------------------')
                print(c_n)
                print('----------------------------------------')

                c_n += 1
                tn.write('diagnostic selt show {0}-{1}\n'.format(self.port_conditions['slot_number'], self.port_conditions['port_number']).encode('utf-8'))
                tn.write((str(prompt)+str(c_n)+"\r\n").encode('utf-8'))
                output = tn.read_until((str(prompt)+str(c_n)).encode('utf-8'))
            # output = output.replace(self.__clear_port_name(output),'')
            if self.request_from_ui:
                return dict(result=output.decode('utf-8'), status=200)
            result = str(output).split("\\r\\n")
            result = [val for val in result if re.search(r'kFt', val)]
            result = [re.sub(r'\s{2,}', ',', val) for val in result][0].split(",")
            results.append(
                dict(port={'card': self.port_conditions['slot_number'], 'port': self.port_conditions['port_number']},
                     inprogress=result[1], cableType=result[2],
                     loopEstimateLength=result[3]))
            tn.write(b'exit\r\n')
            tn.write(b"y\r\n")
            tn.close()
            return dict(result=results, status=200)
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno)))
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
