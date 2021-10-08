import telnetlib
import time
from socket import error as socket_error
from command_base import BaseCommand
import re


class ShowSlotPortByMac(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__mac = params.get('mac')

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
        results = []
        try:
            tn = telnetlib.Telnet(self.__HOST)
            if tn.read_until('>>User name:'):
                tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if tn.read_until('>>User password:'):
                tn.write((self.__telnet_password + "\r\n\r\n").encode('utf-8'))

            tn.write("\r\n\r\n")
            tn.write("\r\n\r\n")
            tn.write("enable\r\n")
            tn.write("config\r\n")
            tn.write("display mac-address all\r\n".encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))
            tn.write(("\r\n\r\n").encode('utf-8'))

            result = tn.read_until("Note")
            mac_add = []
            macObj = []
            for item in result.split('\r\n'):
                mac_add.append(item.split())
            for item2 in mac_add:
                if 'dynamic' in item2:
                    case = {item2[1]: item2[3].split('/')[1]}
                    macObj.append(case)
            for item3 in macObj:
                for mac, card in item3.items():
                    if mac == self.__mac:
                        slot = card
                        for x in range(50):
                            tn.write(("display mac-address port 0/{0}/{1}\r\n".format(str(slot), str(x))))
                            tn.write('end\r\n')
                            result = tn.read_until("end")
                            if (self.__mac in result):
                                return {'Card / port': str(slot) + ' / ' + str(x)}
                        return {'result': 'Port Not Found.'}
                    else:
                        slot = -1

            tn.write(("\r\n").encode('utf-8'))
            com = re.compile(
                r'(?P<mac>\w{4}-\w{4}-\w{4})\s+\S+\s+\d{1}(\s)?/(?P<slot_number>\d+)(\s/(?P<port_number>\d+)\s+['
                r'\d+|\-]+\s+[\d+|\-]+)?\s+(?P<vlan_id>(\d+|\w+))')
            results = [m.groupdict() for m in com.finditer(result)]
            tn.write("quit\r\n")
            tn.write("y\r\n")
            tn.close()
            return {'result': slot}
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
