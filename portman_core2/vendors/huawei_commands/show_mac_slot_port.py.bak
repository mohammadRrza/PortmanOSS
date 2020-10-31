import telnetlib
import time
from socket import error as socket_error
from command_base import BaseCommand
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
        print 'start run command'
        results = []
        try:
            tn = telnetlib.Telnet(self.__HOST)
            if tn.read_until('>>User name:'):
                tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if tn.read_until('>>User password:'):
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write("enable\r\n")
            #tn.write("enable\r\n")
            tn.write("config\r\n")
            for port_item in self.__port_indexes:
                tn.write(("display mac-address adsl 0/{0}/{1}\r\n".format(port_item['slot_number'], port_item['port_number'])).encode('utf-8'))
                #tn.write(("display mac-address port 0/{0}/{1}\r\n".format(port_item['slot_number'], port_item['port_number'])).encode('utf-8'))
            tn.write('end\r\n')
            result = tn.read_until("end")
            items = re.findall(r'(\w{4}-\w{4}-\w{4})\s+\S+\s+\d{1}\s/(\d{1,2})\s/(\d{1,2})\s+\d+\s+\d+\s+(\d+)',result)
            for mac, slot, port, vlan_id in items:
                results.append({
                    "mac": mac,
                    "vlan_id": vlan_id,
                    "slot": slot,
                    "port": port
                    })

            if not bool(results):
                results.append({'result': "don't have any mac"})

            tn.write("quit\r\n")
            tn.write("y\r\n")
            tn.close()
            print '***********************'
            print results
            print '***********************'
            return {'result': results}
        except (EOFError,socket_error) as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception,e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
