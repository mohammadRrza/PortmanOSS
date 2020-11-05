import telnetlib
import time
from socket import error as socket_error
from command_factory import CommandFactory
from zyxel_commands.selt import Selt
from zyxel_commands.show_mac_slot_port import ShowMacSlotPort
from zyxel_commands.lcman_show import LcmanShow
from zyxel_commands.profile_adsl_show import ProfileADSLShow
from zyxel_commands.create_profile import CreateProfile
from zyxel_commands.delete_profile import DeleteProfile
from zyxel_commands.lcman_disable_slot import LcmanDisableSlot
from zyxel_commands.lcman_reset_slot import LcmanResetSlot
from zyxel_commands.lcman_enable_slot import LcmanEnableSlot
from zyxel_commands.lcman_show_slot import LcmanShowSlot
from zyxel_commands.port_disable import PortDisable
from zyxel_commands.port_enable import PortEnable
from zyxel_commands.port_pvc_set import PortPvcSet
from zyxel_commands.port_pvc_delete import PortPvcDelete
from zyxel_commands.add_to_vlan import AddToVlan
from zyxel_commands.create_vlan import CreateVlan
from zyxel_commands.vlan_show import VlanShow

class ZyxelTelnet(object):
    retry = 1
    command_factory = CommandFactory()
    command_factory.register_type('selt', Selt)
    command_factory.register_type('show mac slot port', ShowMacSlotPort)
    command_factory.register_type('profile adsl show', ProfileADSLShow)
    command_factory.register_type('lcman show', LcmanShow)
    command_factory.register_type('profile adsl set', CreateProfile)
    command_factory.register_type('profile adsl delete', DeleteProfile)
    command_factory.register_type('lcman disable slot', LcmanDisableSlot)
    command_factory.register_type('lcman reset slot', LcmanResetSlot)
    command_factory.register_type('lcman enable slot', LcmanEnableSlot)
    command_factory.register_type('lcman show slot', LcmanShowSlot)
    command_factory.register_type('port disable', PortDisable)
    command_factory.register_type('port enable', PortEnable)
    command_factory.register_type('port pvc set', PortPvcSet)
    command_factory.register_type('port pvc delete', PortPvcDelete)
    command_factory.register_type('add to vlan', AddToVlan)
    command_factory.register_type('create vlan', CreateVlan)
    command_factory.register_type('vlan show', VlanShow)

    def __init__(self, dslam_data, zyxel_q):
        self.__host = dslam_data.get('ip')
        self.__telnet_username = dslam_data.get('telnet_username')
        self.__telnet_password = dslam_data.get('telnet_password')
        self.tn = self.open_connection()
        self.zyxel_q = zyxel_q

    def open_connection(self):
        print 'try to open connections'
        try:
            tn = telnetlib.Telnet(self.__host)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if self.__telnet_password:
                tn.read_until("Password: ")
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            print 'open connection dslam with ip: {0}'.format(self.__host)
            return tn
        except (EOFError, socket_error) as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.open_connection()
        except Exception as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.open_connection()

    def run_command(self, command, params):
        try:
            self.tn.read_very_eager()
            command_class = self.command_factory.get_type(command)(self.tn, params, self.zyxel_q)
            command_thread = Thread(target=command_class.run_command)
            command_thread.start()
        except Exception as e:
            print e
            self.tn = self.open_connection()
            return self.run_command(command, params)
