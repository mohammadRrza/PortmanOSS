import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowMacSlotPort(BaseCommand):
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
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)
            results = []
            tn.write("show mac {0}-{1}\r\n\r\n".format(self.port_conditions['slot_number'],
                                                       self.port_conditions['port_number']).encode("utf-8"))
            time.sleep(0.5)
            tn.write(b"end\r\n")
            result = tn.read_until(b'end')
            if "example:" in str(result):
                result = str(result).split("\\r\\n")
                result = [val for val in result if re.search(r'example|between', val)]
                return dict(resutl=result, status=500)
            if "inactive" in str(result):
                result = str(result).split("\\r\\n")
                result = [val for val in result if re.search(r'inactive', val)]
                return dict(resutl=result, status=500)
            if "giga-port" in str(result):
                return dict(resutl="Card or Port number is out of range.", status=500)
            if "vid" not in str(result):
                return dict(resutl="There is no MAC Address on this port", status=500)
            #     com = re.compile(r'(?P<vlan_id>\s(\d{1,10}))(\s)*(?P<mac>([0-9A-F]{2}[:-]){5}([0-9A-F]{2}))(\s)*(?P<port>(\d{1,3})?-(\s)?(\d{1,3})?)',re.MULTILINE | re.I)
            #     port = com.search(result).group('port').split('-')[1].strip()
            #     slot = com.search(result).group('port').split('-')[0].strip()
            #     vlan_id = com.search(result).group('vlan_id')
            #     mac = com.search(result).group('mac')
            #     results.append({
            #         "mac": mac.strip(),
            #         #"vlan_id": vlan_id.strip(),
            #         "slot": slot.strip(),
            #         "port": port.strip()
            #         })
            # if not bool(results):
            #     results.append({'result': "don't have any mac"})
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('***********************')
            print(results)
            print('***********************')
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=result.decode('utf-8'), status=200)
            result = str(result).split("\\r\\n")
            result = [val for val in result if re.search(r'\S:\S', val)][0].split()
            result = dict(
                port={'card': self.port_conditions['slot_number'], 'port': self.port_conditions['port_number']},
                vid=result[0], mac=result[1])
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
