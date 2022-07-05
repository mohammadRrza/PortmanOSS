import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowPort(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__access_name = params.get('access_name', 'an2100')
        self.__port_indexes = params.get('port_indexes')
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

    def process_telnet_option(self, tsocket, command, option):
        from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS, LINEMODE, ECHO
        tsocket.sendall(IAC + WONT + LINEMODE)

    retry = 1

    def run_command(self):
        try:
            print("+++++++++++++++++++++++++++")
            tn = telnetlib.Telnet(self.__HOST, timeout=5)
            tn.set_option_negotiation_callback(self.process_telnet_option)
            print('send login ...')
            tn.write('{0}\r\n'.format(self.__access_name).encode("utf-8"))
            err1 = tn.read_until(b"correct", 2)
            if "incorrect" in str(err1):
                tn.close()
                return dict(result="Access name is wrong!", status=500)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            err2 = tn.read_until(b"Password:", 2)
            if "Invalid User Name" in str(err2):
                tn.close()
                return dict(result="User Name is wrong.", status=500)
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err3 = tn.read_until(b"OK!", 2)
            if "Invalid Password" in str(err3):
                tn.close()
                return dict(result="Password is wrong.", status=500)
            print('password sent ...')
            tn.write(b"line\r\n")
            tn.write(b"sp\r\n")
            tn.read_until(b'(xx-xx)', 2)
            tn.write("0-{0} \r\n".format(self.port_conditions['slot_number']).encode('utf-8'))
            time.sleep(0.5)
            err4 = tn.read_until(b'(default is 1~32)', 2)
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
            time.sleep(1)
            tn.write(b"\r\n")
            tn.write(b"finish")
            res = tn.read_until(b'finish', 2)
            tn.close()
            if "timeout!!" in str(res):
                return dict(result="Timeout! Please try again.", status=500)
            if "The port is" in str(res):
                return dict(result=f"Port number '{self.port_conditions['port_number']}' is out of range. Please insert a number between 1-32", status=500)
            if "handshake" in str(res):
                return dict(result="Port is Down", status=500)
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=res.decode('utf-8'), status=200)
            result = str(res).split("\\n\\r")
            result = [val for val in result if re.search(r'\s+:|--+', val)]

            res = {'dslamName/cammandName': "",
                   'date': "",
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
                if "Stream SNR_Margin" in val:
                    res['noisemarginUp'] = val.split(":")[1].split("/")[1].split(" ")[0]
                    res['noisemarginDown'] = val.split(":")[1].split("/")[0].strip()
                if "Attainable rate" in val:
                    res['attainablerateUp'] = val.split(":")[1].split("/")[1].split(" ")[0]
                    res['attainablerateDown'] = val.split(":")[1].split("/")[0].strip()
                if "Rate(D/U)" in val:
                    res['payloadrateUp'] = val.split(":")[1].split("/")[1].split(" ")[0]
                    res['payloadrateDown'] = val.split(":")[1].split("/")[0].strip()
                if "Stream attenuation" in val:
                    res['attenuationUp'] = val.split(":")[1].split("/")[1].split(" ")[0]
                    res['attenuationDown'] = val.split(":")[1].split("/")[0].strip()

            return dict(result=res, status=200)
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
