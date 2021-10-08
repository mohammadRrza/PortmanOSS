import telnetlib
import time
from socket import error as socket_error
from command_base import BaseCommand
import re

class AclMaccountSet(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__vpi = params.get('vpi')
        self.__vci = params.get('vci')
        self.__port_indexes = params.get('port_indexes')
        self.__count = params.get('count')

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
            results = []
            for port_item in self.__port_indexes:
                tn.write(("acl maccount set {slot_number}-{port_number}-{vpi}/{vci} {count}\r\n".format(\
                        slot_number = port_item['slot_number'],
                        port_number = port_item['port_number'],
                        vpi = self.__vpi,
                        vci = self.__vci,
                        count = self.__count
                        )).encode("utf-8"))
                time.sleep(1)
                tn.write(("acl maccount set {slot_number}-{port_number} {count}\r\n".format(\
                        slot_number = port_item['slot_number'],
                        port_number = port_item['port_number'],
                        count = self.__count
                    )).encode("utf-8"))
                time.sleep(1)
            tn.write("end\r\n")
            result = tn.read_until('end')
            tn.write("exit\r\n")
            tn.write("y\r\n")
            tn.close()
            return {'result': "acl maccount set {slot_number}-{port_number} {count}\r\n".format(\
                        slot_number = port_item['slot_number'],
                        port_number = port_item['port_number'],
                        count = self.__count
                    )}
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
