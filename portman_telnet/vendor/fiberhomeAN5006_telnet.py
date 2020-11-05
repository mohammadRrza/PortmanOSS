import telnetlib
import time
import sys
import os
import traceback
from socket import error as socket_error
from .command_factory import CommandFactory
from .fiberhomeAN5006_commands.port_enable import PortEnable
from .fiberhomeAN5006_commands.port_disable import PortDisable
from .fiberhomeAN5006_commands.show_cart import ShowCart
from .fiberhomeAN5006_commands.show_shelf import ShowShelf
from .fiberhomeAN5006_commands.show_port import ShowPort
from .fiberhomeAN5006_commands.show_temperature import ShowTemperature

class FiberhomeAN5006Telnet(object):
    retry = 1
    command_factory = CommandFactory()
    command_factory.register_type('port enable', PortEnable)
    command_factory.register_type('port disable', PortDisable)
    command_factory.register_type('show cart', ShowCart)
    command_factory.register_type('show shelf', ShowShelf)
    command_factory.register_type('show port', ShowPort)
    command_factory.register_type('show temperature', ShowTemperature)

    def __init__(self,telnet_dict, dslam_data, fiberhomeAN5006_q):
        self.__host = dslam_data.get('ip')
        self.__telnet_username = dslam_data.get('telnet_username')
        self.__telnet_password = dslam_data.get('telnet_password')
        self.tn = self.open_connection()
        self.fiberhomeAN5006_q = fiberhomeAN5006_q
        self.telnet_dict = telnet_dict

    def open_connection(self):
        self.retry += 1
        print('try to open connections')
        print(self.__host)
        print(self.__telnet_username)
        print(self.__telnet_password)
        try:
            tn = telnetlib.Telnet(self.__host)
            tn.read_until("Login: ")
            tn.write("{0}\r\n".format(self.__telnet_username).encode('utf-8'))
            if self.__telnet_password:
                tn.read_until("Password: ")
                tn.write("{0}\r\n".format(self.__telnet_password).encode('utf-8'))
            tn.read_until("#")
            print('open connection dslam with ip: {0}'.format(self.__host))
            return tn
        except (EOFError, socket_error) as e:
            print(e)
            if self.retry < 4:
                return self.open_connection()
        except Exception as e:
            print(e)
            if self.retry < 4:
                return self.open_connection()

    def run_command(self, command, params, protocol='socket'):
        try:
            print('------------------------------------------')
            print('run command {0}'.format(command))
            print('------------------------------------------')
            self.tn.read_very_eager()
            command_class = self.command_factory.get_type(command)(self.tn, params, self.fiberhomeAN5006_q)
            return command_class.run_command(protocol)

        except Exception as e:
            self.retry += 1
            import sys
            import os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(traceback.format_exc())
            print(exc_type, fname, exc_tb.tb_lineno)
            if self.retry < 4:
                self.tn = self.open_connection()
                return self.run_command(command, params)
            else:
                if self.dslam_id in list(self.telnet_dict.keys()):
                    del self.telnet_dict[self.dslam_id]
