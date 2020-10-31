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

    retry = 1
    def run_command(self):
        print('start run command')
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            results = []
            for port_item in self.__port_indexes:
                tn.write("show mac {0}-{1}\r\n\r\n".format(port_item['slot_number'], port_item['port_number']).encode("utf-8"))
                time.sleep(2)
                tn.write("end\r\n")
                result = tn.read_until('end')
                print(result)
                com = re.compile(r'(?P<vlan_id>\s(\d{1,10}))(\s)*(?P<mac>([0-9A-F]{2}[:-]){5}([0-9A-F]{2}))(\s)*(?P<port>(\d{1,3})?-(\s)?(\d{1,3})?)',re.MULTILINE | re.I)
                port = com.search(result).group('port').split('-')[1].strip()
                slot = com.search(result).group('port').split('-')[0].strip()
                vlan_id = com.search(result).group('vlan_id')
                mac = com.search(result).group('mac')
                results.append({
                    "mac": mac.strip(),
                    #"vlan_id": vlan_id.strip(),
                    "slot": slot.strip(),
                    "port": port.strip()
                    })
            if not bool(results):
                results.append({'result': "don't have any mac"})
            tn.write("exit\r\n")
            tn.write("y\r\n")
            tn.close()
            print('***********************')
            print(results)
            print('***********************')
            return {'result': results}
        except (EOFError,socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
