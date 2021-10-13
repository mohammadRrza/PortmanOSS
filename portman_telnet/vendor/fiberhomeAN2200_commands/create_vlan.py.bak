import telnetlib
import re
import time
from base_command import BaseCommand

class CreateVlan(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN2200_q', 'dslam_id', 'vlan_name', 'vlan_id', 'untagged_port')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')
        self.vlan_name = params.get('vlan_name')
        self.vlan_id = params.get('vlan_id')
        self.untagged_port = params.get('untagged_port')

    def run_command(self):
        try:
            self.tn.write("ip\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            self.tn.write("createvlan\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            time.sleep(1)
            self.tn.write(self.vlan_name+"\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write(self.vlan_id+"\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write("\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write(self.untagged_port+"\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write("n\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write("n\r\n".encode('utf-8'))
            time.sleep(1)
            output = self.tn.read_until('>',5)
            print '==================================='
            print output
            print '==================================='
            result = ''
            self.tn.write("exit\r\n\r\n")
            self.tn.close()

            if 'Create vlan' in output:
                result = {'result': '{0} created valn'.format(self.vlan_name)}

            if protocol == 'http':
                return result
            elif protocol == 'socket':
                self.fiberhomeAN2200_q.put((
                    "update_dslamport_command_result",
                    self.dslam_id,
                    self.port_indexes,
                    "add to vlan",
                    result))

        except Exception as ex:
            print ex
            return "error: {0} created valn".format(self.__vlan_name)
