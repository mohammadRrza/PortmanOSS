import time
from datetime import datetime
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from vendors.base import BaseDSLAM
from easysnmp import Session
import re
from .command_factory import CommandFactory
from .zyxel_commands.show_mac import ShowMac
from .zyxel_commands.vlan_show import VlanShow
from datetime import timedelta

class Zyxel(BaseDSLAM):

    command_factory = CommandFactory()
    command_factory.register_type('show mac', ShowMac)
    command_factory.register_type('vlan show', VlanShow)

    EVENT = {'dslam_connection_error':'DSLAM Connection Error', 'no_such_object':'No Such Objects'}
    EVENT_INVERS = dict(list(zip(list(EVENT.values()),list(EVENT.keys()))))


    @classmethod
    def execute_command(cls, dslam_info, command, params=None):
        if params:
            params['set_snmp_community'] = dslam_info['set_snmp_community']
            params['get_snmp_community'] = dslam_info['get_snmp_community']
        command_class = cls.command_factory.get_type(command)(params)
        command_class.HOST = dslam_info['ip']
        command_class.telnet_username = dslam_info['telnet_username']
        command_class.telnet_password = dslam_info['telnet_password']
        return command_class.run_command()
