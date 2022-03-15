import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowPerformance(BaseCommand):
    def __init__(self, params):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_indexes = params.get('port_indexes')
        self.__time_elapsed = params.get('time_elapsed')
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
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.read_until(b"Password:")
            results = []
            for port_item in self.__port_indexes:
                tn.write(
                    "show performance {0}-{1} {2}\r\n\r\n".format(port_item['slot_number'], port_item['port_number'],
                                                                  self.__time_elapsed).encode('utf-8'))
                time.sleep(1)
                for item in range(7):
                    time.sleep(1)
                    tn.write(b"n\r\n")
                    tn.write(b"next\r\n")
                    tn.read_until(b"Communications Corp.")
                    result = tn.read_until(b"next")
                    if b'next' in result:
                        results.append(result)
                        break
            results = b'\r\n'.join(results).split(b'n\r\nn: invalid command')[0]
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            print('******************************************')
            print(("show performance {0}".format(results)))
            print('******************************************')
            return dict(result=b'\r\n'.join(results.split(b'\r\n')[:50]), status=200)
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
