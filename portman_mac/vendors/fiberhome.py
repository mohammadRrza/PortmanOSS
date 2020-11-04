import time
from datetime import datetime
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from vendors.base import BaseDSLAM
from easysnmp import Session
import re
from .command_factory import CommandFactory
from .fiberhome_commands.show_mac import ShowMac
from datetime import timedelta

class Fiberhome(BaseDSLAM):

    command_factory = CommandFactory()
    command_factory.register_type('show mac', ShowMac)

    EVENT = {'dslam_connection_error':'DSLAM Connection Error', 'no_such_object':'No Such Objects'}
    EVENT_INVERS = dict(list(zip(list(EVENT.values()),list(EVENT.keys()))))


    @classmethod
    def execute_command(cls, dslam_info, command, params):
        params['set_snmp_community'] = dslam_info['set_snmp_community']
        params['get_snmp_community'] = dslam_info['get_snmp_community']
        if dslam_info.get('access'):
            params['access'] = dslam_info.get('access')
        command_class = cls.command_factory.get_type(command)(params)
        command_class.HOST = dslam_info['ip']
        command_class.telnet_username = dslam_info['telnet_username']
        command_class.telnet_password = dslam_info['telnet_password']
        return command_class.run_command()
