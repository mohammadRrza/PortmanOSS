import datetime
import os
import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowLineRate(BaseCommand):
    def __init__(self, params):
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

    def __clear_port_name(self, port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern, port_name, re.M | re.DOTALL)
        return st.group()

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)
            tn.write("show linerate {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'],
                                                            self.port_conditions['port_number']).encode(
                'utf-8'))
            time.sleep(1)
            tn.write(b'end1\r\n')
            result = tn.read_until(b'end1')
            if "example:" in str(result):
                result = str(result).split("\\r\\n")
                result = [val for val in result if re.search(r'example|between', val)]
                return dict(result=result, status=500)
            if "inactive" in str(result):
                result = str(result).split("\\r\\n")
                result = [val for val in result if re.search(r'inactive', val)]
                return dict(result=result, status=500)
            tn.write(b'exit\r\n')
            tn.write(b'y\r\n')
            tn.close()
            # print('*******************************************')
            # print(('show linerate {0}'.format(str(result))))
            # print('*******************************************')
            if self.device_ip == '127.0.0.1' or self.device_ip == '185.126.18.160':
                return dict(result=result.decode('utf-8'), status=200)
            result = str(result).split("\\r\\n")
            res = {'dslamName/cammandName': "",
                   'date': str(datetime.datetime.now()),
                   'slot/port': str(self.port_conditions['slot_number']) + '-' + str(
                       self.port_conditions['port_number']),
                   # 'OP_State' : res[4].split(":")[1],
                   # 'Standard' : res[5].split(":")[1],
                   # 'Latency' : res[6].split(":")[1],
                   'noisemarginDown': "",
                   'noisemarginUp': "",
                   'payloadrateDown': "",
                   'payloadrateUp': "",
                   'attenuationDown': "",
                   'attenuationUp': "",
                   # 'Tx power(D/U)' : res[10].split(":")[1].split("/")[0],
                   # 'Tx power(D/U)' : res[10].split(":")[1].split("/")[1].split(" ")[0],
                   # 'Remote vendor ID' : res[11].split(":")[1],
                   # 'Power management state' : res[12].split(":")[1],
                   # 'Remote vendor version ID' : res[13].split(":")[1],
                   # 'Loss of power(D)' : res[14].split(":")[1].split("/")[0],
                   # 'Loss of power(U)' : res[14].split(":")[1].split("/")[1].split(" ")[0],
                   # 'Loss of signal(D)' : res[15].split(":")[1].split("/")[0],
                   # 'Loss of signal(U)' : res[15].split(":")[1].split("/")[1].split(" ")[0],
                   # 'Error seconds(D)' : res[16].split(":")[1].split("/")[0],
                   # 'Error seconds(U)' : res[16].split(":")[1].split("/")[1].split(" ")[0],
                   # 'Loss by HEC collision(D)' : res[17].split(":")[1].split("/")[0],
                   # 'Loss by HEC collision(U)' : res[17].split(":")[1].split("/")[1].split(" ")[0],
                   # 'Forward correct(D)' : res[18].split(":")[1].split("/")[0],
                   # 'Forward correct(U)' : res[18].split(":")[1].split("/")[1],
                   # 'Uncorrect(D)' : res[19].split(":")[1].split("/")[0],
                   # 'Uncorrect(U)' : res[19].split(":")[1].split("/")[1],
                   'attainablerateDown': "",
                   'attainablerateUp': "",
                   'actualrateDown': "",
                   'actualrateUp': "",

                   # 'Interleaved Delay(D) ' : res[21].split(":")[1].split("/")[0],
                   # 'Interleaved Delay(U) ' : res[21].split(":")[1].split("/")[1],
                   # 'Remote loss of link' : res[22].split(":")[1],
                   }

            for inx, val in enumerate(result):
                if "noise margin" in val:
                    res['noisemarginUp'] = val.split("=")[1].split()[0]
                    res['noisemarginDown'] = val.split("=")[1].split()[1]
                if "attainable rate" in val:
                    res['attainablerateUp'] = val.split("=")[1].split()[0]
                    res['attainablerateDown'] = val.split("=")[1].split()[1]
                if "actual rate" in val:
                    res['actualrateUp'] = val.split("=")[1].split()[0]
                    res['actualrateDown'] = val.split("=")[1].split()[1]
                if "attenuation" in val:
                    res['attenuationUp'] = val.split("=")[1].split()[0]
                    res['attenuationDown'] = val.split("=")[1].split()[1]
                if "payload rate" in val:
                    res['payloadrateUp'] = val.split("=")[1].split()[0]
                    res['payloadrateDown'] = val.split("=")[1].split()[1]
                if "link" in val:
                    res['link'] = val.split("=")[1].strip()

            return dict(result=res, status=200)
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno)))
            # print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
