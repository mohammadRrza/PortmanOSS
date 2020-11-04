import csv
import telnetlib
import re
import time
from base_command import BaseCommand

class DelFromVlan(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN2200_q', 'dslam_id', 'vlan_name', 'vlan_id'\
            'port_indexes', 'untagged_port')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')
        self.vlan_name = params.get('vlan_name')
        self.vlan_id = params.get('vlan_id')
        self.port_indexes = params.get('port_indexes')
        self.untagged_port = params.get('untagged_port','20')

    def run_command(self, protocol):
        try:
            self.tn.write("ip\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            self.tn.write("delfromvlan\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            for port_item in self.port_indexes:
                self.tn.write(self.vlan_name+"\r\n".encode('utf-8'))
                time.sleep(1)
                self.tn.write("0-{0}-{1}\r\n".format(port_item.get('slot_number'), port_item.get('port_number')).encode('utf-8'))
                time.sleep(1)
                self.tn.write('0-{0}\r\n'.format(self.untagged_port).encode('utf-8'))
                time.sleep(1)
                self.tn.write("Y\r\n".encode('utf-8'))
                time.sleep(1)
            else:
                self.tn.write("exit\r\n".encode('utf-8'))
            output = self.tn.read_until('>',5)
            result = ''
            if 'Tag port to be deleted' in output:
                result ={'result': "{0} deleted from valn {1}".format(self.port_indexes, self.vlan_name)}
            print '==================================='
            print result
            print '==================================='
            self.tn.write("exit\r\n\r\n")
            self.tn.close()

            if protocol == 'http':
                return result
            elif protocol == 'socket':
                self.fiberhomeAN2200_q.put((
                    "update_dslamport_command_result",
                    self.dslam_id,
                    self.port_indexes,
                    "add to vlan",
                    result))

        except Exception as e:
            print e
            return "error: {0} deleted from valn {1}".format(self.__port_name, self.__vlan_name)
