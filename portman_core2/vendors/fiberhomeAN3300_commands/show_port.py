import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowPort(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__vlan_name = params.get('vlan_name')
        self.__access_name = params.get('access_name', 'an3300')
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
            tn.write(b"end\r\n")
            err1 = tn.read_until(b"end")
            if "Login Failed." in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.read_until(b"User>")
            tn.write(b'admin\r\n')
            tn.read_until(b"Password:")
            tn.write('{0}\r\n'.format(self.__access_name).encode('utf-8'))
            time.sleep(0.5)
            err1 = tn.read_until(b"#", 1)
            if "Bad Password..." in str(err1):
                return "DSLAM Password is wrong!"
            tn.write(b"cd device\r\n")
            tn.write("show port {0}:{1}\r\n\r\n".format(self.port_conditions['slot_number'],
                                                        self.port_conditions['port_number']).encode('utf-8'))
            time.sleep(0.1)
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            time.sleep(0.1)
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=result.decode('utf-8'), status=200)
            if "Invalid port list" in str(result):
                str_res = ["There is one of the following problems:", "This card is not configured",
                           "No card is defined on this port", "Card number is out of range.",
                           "Port number is out of range."]
                return str_res
            if "Handshake" in str(result):
                return "Port is down"
            tn.close()
            result = str(result).split("\\r\\n")
            result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+H', '', val) for val in result if
                      re.search(r'\s{3,}', val)]
            # d = {}
            # for b in result:
            #     if ": " in b:
            #         i = b.split(': ', 1)
            #         d[i[0].strip()] = i[1].strip()
            # result = d

            res = {'current_userProfile': "",
                   'dslamName/cammandName': "",
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
                if "DownStream Margin" in val:
                    res['noisemarginUp'] = val.split(":")[2].strip()
                    res['noisemarginDown'] = val.split(":")[1].split()[0]
                if "DownStream attain rate" in val:
                    res['attainablerateUp'] = val.split(":")[2].strip()
                    res['attainablerateDown'] = val.split(":")[1].split()[0]
                if "DownStream rate" in val:
                    res['payloadrateUp'] = val.split(":")[2].strip()
                    res['payloadrateDown'] = val.split(":")[1].split()[0]
                if "DownStream Attenuat" in val:
                    res['attenuationUp'] = val.split(":")[2].strip()
                    res['attenuationDown'] = val.split(":")[1].split()[0]

            return dict(result=res, status=200)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as e:
            print(e)
            return str(e)
