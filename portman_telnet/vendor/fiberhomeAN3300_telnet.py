import telnetlib
import time
from socket import error as socket_error
import traceback
from .command_factory import CommandFactory
from .fiberhomeAN3300_commands.show_fdb_slot import ShowFdbSlot
from .fiberhomeAN3300_commands.port_enable import PortEnable
from .fiberhomeAN3300_commands.port_disable import PortDisable
from .fiberhomeAN3300_commands.get_ports_status import GetPortsStatus
from .fiberhomeAN3300_commands.get_current_port_status import GetCurrentPortStatus
from .fiberhomeAN3300_commands.get_dslam_board import GetDSLAMBoard

class FiberhomeAN3300Telnet(object):
    retry = 1
    command_factory = CommandFactory()
    command_factory.register_type('show mac', ShowFdbSlot)
    command_factory.register_type('port enable', PortEnable)
    command_factory.register_type('port disable', PortDisable)
    command_factory.register_type('get ports status', GetPortsStatus)
    command_factory.register_type('get dslam board', GetDSLAMBoard)
    command_factory.register_type('get current port status', GetCurrentPortStatus)

    def __init__(self, telnet_dict, dslam_data, fiberhomeAN3300_q):
        self.__host = dslam_data.get('ip')
        self.__telnet_username = dslam_data.get('telnet_username')
        self.__telnet_password = dslam_data.get('telnet_password')
        self.tn = self.open_connection()
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.telnet_dict = telnet_dict

    def open_connection(self):
        self.retry += 1
        print('try to open connections')
        try:
            tn = telnetlib.Telnet(self.__host)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if self.__telnet_password:
                tn.read_until("Password: ")
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.write(("admin\r\n").encode('utf-8'))
            tn.read_until("Password: ")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            data = tn.read_until("#")
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
            self.tn.read_very_eager()
            command_class = self.command_factory.get_type(command)(self.tn, params, self.fiberhomeAN3300_q)
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
