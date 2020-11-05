import telnetlib
import traceback
import time
from socket import error as socket_error
from threading import Thread
from command_factory import CommandFactory
from fiberhomeAN2200_commands.show_mac_slot_port import ShowMacSlotPort
#from fiberhomeAN2200_commands.lcman_show import LcmanShow
from fiberhomeAN2200_commands.profile_adsl_show import ProfileADSLShow
from fiberhomeAN2200_commands.create_profile import CreateProfile
from fiberhomeAN2200_commands.delete_profile import DeleteProfile
from fiberhomeAN2200_commands.add_to_vlan import AddToVlan
from fiberhomeAN2200_commands.port_disable import PortDisable
from fiberhomeAN2200_commands.port_reset import PortReset
from fiberhomeAN2200_commands.port_enable import PortEnable
from fiberhomeAN2200_commands.port_pvc_set import PortPvcSet
from fiberhomeAN2200_commands.port_pvc_delete import PortPvcDelete
from fiberhomeAN2200_commands.create_vlan import CreateVlan
from fiberhomeAN2200_commands.vlan_show import VlanShow
from fiberhomeAN2200_commands.change_profile import ChangeProfile
from fiberhomeAN2200_commands.uplink_pvc_delete import UpLinkPvcDelete
from fiberhomeAN2200_commands.uplink_pvc_set import UpLinkPvcSet
from fiberhomeAN2200_commands.uplink_pvc_show import UpLinkPvcShow
from fiberhomeAN2200_commands.get_ports_status import GetPortsStatus
from fiberhomeAN2200_commands.get_dslam_board import GetDSLAMBoard
from fiberhomeAN2200_commands.get_ports_vpi_vci import GetPortsVpiVci
from fiberhomeAN2200_commands.lcman_reset_slot import LcmanResetSlot
from fiberhomeAN2200_commands.dslam_up_time import DSLAMUpTime
from fiberhomeAN2200_commands.open_port_selt import OpenPortSelt
from fiberhomeAN2200_commands.show_port_selt import ShowPortSelt
from fiberhomeAN2200_commands.show_hostname import ShowHostname
from fiberhomeAN2200_commands.get_current_port_status import GetCurrentPortStatus

'''from fiberhomeAN2200_commands.lcman_disable_slot import LcmanDisableSlot
from fiberhomeAN2200_commands.lcman_enable_slot import LcmanEnableSlot
from fiberhomeAN2200_commands.lcman_show_slot import LcmanShowSlot
'''

class FiberhomeAN2200Telnet(object):
    retry = 1
    command_factory = CommandFactory()
    command_factory.register_type('show mac slot port', ShowMacSlotPort)
    command_factory.register_type('profile adsl show', ProfileADSLShow)
    command_factory.register_type('add to vlan', AddToVlan)
    command_factory.register_type('port disable', PortDisable)
    command_factory.register_type('port reset', PortReset)
    command_factory.register_type('port enable', PortEnable)
    command_factory.register_type('loop to wan vc', PortPvcSet)
    command_factory.register_type('port pvc delete', PortPvcDelete)
    command_factory.register_type('create vlan', CreateVlan)
    command_factory.register_type('vlan show', VlanShow)
    command_factory.register_type('get ports status', GetPortsStatus)
    command_factory.register_type('get dslam board', GetDSLAMBoard)
    command_factory.register_type('get ports vpi vci', GetPortsVpiVci)
    command_factory.register_type('profile adsl set', CreateProfile)
    command_factory.register_type('profile adsl delete', DeleteProfile)
    command_factory.register_type('profile adsl change', ChangeProfile)
    command_factory.register_type('uplink pvc delete', UpLinkPvcDelete)
    command_factory.register_type('uplink pvc set', UpLinkPvcSet)
    command_factory.register_type('uplink pvc show slot', UpLinkPvcShow)
    command_factory.register_type('uplink pvc show', UpLinkPvcShow)
    command_factory.register_type('lcman reset slot', LcmanResetSlot)
    command_factory.register_type('dslam up time', DSLAMUpTime)
    command_factory.register_type('open port selt', OpenPortSelt)
    command_factory.register_type('show port selt', ShowPortSelt)
    command_factory.register_type('show hostname', ShowHostname)
    command_factory.register_type('get current port status', GetCurrentPortStatus)

    '''
    command_factory.register_type('lcman disable slot', LcmanDisableSlot)
    command_factory.register_type('lcman show', LcmanShow)
    command_factory.register_type('lcman enable slot', LcmanEnableSlot)
    command_factory.register_type('lcman show slot', LcmanShowSlot)
    '''

    def __init__(self, telnet_dict, dslam_data, fiberhomeAN2200_q=None):
        print telnet_dict, dslam_data
        self.__host = dslam_data.get('ip')
        self.__telnet_username = dslam_data.get('telnet_username')
        self.__telnet_password = dslam_data.get('telnet_password')
        self.__access_name = dslam_data.get('access_name')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.tn = self.open_connection()
        self.dslam_id = dslam_data.get('id')
        self.telnet_dict = telnet_dict

    def process_telnet_option(self, tsocket, command, option):
        from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS, LINEMODE, ECHO
        tsocket.sendall(IAC + WONT + LINEMODE)

    def open_connection(self):
        print 'try to open connections'
        try:
            tn = telnetlib.Telnet(self.__host, timeout=5)
            tn.set_option_negotiation_callback(self.process_telnet_option)

            index, match_obj, text = tn.expect(
                        ['[U|u]sername: ', '[L|l]ogin:', '[L|l]oginname:', '[P|p]assword:'])

            if index == 1:
                print 'send login ...'
                tn.write('{0}\r\n'.format(self.__access_name))

            data = tn.read_until('User Name:', 5)
            print 'here'
            print '==>', data
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            print 'user sent ...'
            data = tn.read_until('Password:', 5)
            print '==>', data
            tn.write(( self.__telnet_password + "\r\n").encode('utf-8'))
            print 'password sent ...'

            data = tn.read_until('>', 5)
            print 'got to prompt ...', data
            print 'open connection dslam with ip: {0}'.format(self.__host)
            return tn
        except (EOFError, socket_error) as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.open_connection()
            else:
                if self.dslam_id in self.telnet_dict.keys():
                    del self.telnet_dict[self.dslam_id]

        except Exception as e:
            #print e
            self.retry += 1
            if self.retry < 4:
                return self.open_connection()
            else:
                if self.dslam_id in self.telnet_dict.keys():
                    del self.telnet_dict[self.dslam_id]

    def run_command(self, command, params, protocol='socket'):
        try:
            self.tn.read_very_eager()
            command_class = self.command_factory.get_type(command)(self.tn, params, self.fiberhomeAN2200_q)
            return command_class.run_command(protocol)

        except Exception as e:
            self.retry += 1
            import sys
            import os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print traceback.format_exc()
            #print exc_type, fname, exc_tb.tb_lineno
            if self.retry < 4:
                #print self.__access_name, self.__host, self.__telnet_username, self.__telnet_password
                self.tn = self.open_connection()
                return self.run_command(command, params)
            else:
                if self.dslam_id in self.telnet_dict.keys():
                    del self.telnet_dict[self.dslam_id]
