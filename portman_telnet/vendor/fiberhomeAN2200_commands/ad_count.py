import telnetlib
import time
from socket import error as socket_error
from command_base import BaseCommand
import re

class ADCount(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__profile = params['access']

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

    def process_telnet_option(self, tsocket, command, option):
        from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS, LINEMODE, ECHO
        tsocket.sendall(IAC + WONT + LINEMODE)

    retry = 1
    def run_command(self):
        try:
            tn = telnetlib.Telnet(HOST, timeout=5)
            tn.set_option_negotiation_callback(process_telnet_option)

            index, match_obj, text = tn.expect(
                        ['[U|u]sername: ', '[L|l]ogin:', '[L|l]oginname:', '[P|p]assword:'])

            print(index, match_obj, text)
            if index == 1:
                print('send login ...')
                tn.write('an2100\r\n')

            data = tn.read_until('User Name:')
            print('here')
            print('==>', data)
            tn.write((user + "\r\n").encode('utf-8'))
            print('user sent ...')
            data = tn.read_until('Password:')
            print('==>', data)
            tn.write((password + "\r\n").encode('utf-8'))
            print('password sent ...')

            data = tn.read_until('>')
            print('got to prompt ...', data)
            tn.write("showcard\r\n".encode('utf-8'))
            time.sleep(1)
            result = tn.read_until('>')
            print(result)
            results = result.split('\n')
            AD32 = 0
            AD32_Plus = 0
            for result in results[2:len(results)-4]:
                items = result.split()
                if 'AD32+' in items[3]:
                    AD32_Plus += 1
                elif 'AD32' in items[3]:
                    AD32 += 1
            print('===================================')
            print('AD32: {0}, AD32+: {1}'.format(AD32, AD32_Plus))
            tn.write("exit\r\n\r\n")
            tn.close()
            return 'AD32 Count: {0}, AD32+ Count: {1}'.format(AD32, AD32_Plus)
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                self.run_command()
        except Exception as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                self.run_command()
