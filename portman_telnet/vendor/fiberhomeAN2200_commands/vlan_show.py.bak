import telnetlib
import re
import time
from base_command import BaseCommand

class VlanShow(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN2200_q', 'dslam_id',)
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')
        self.vlan_id = params.get('vlan_id')

    def run_command(self, protocol):
        try:
            self.tn.write("ip\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            self.tn.write("showvlan\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            time.sleep(1)
            self.tn.write("2\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write("\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write("\r\n".encode('utf-8'))
            time.sleep(1)

            output = self.tn.read_until('>',5)

            result = ''
            if 'no vlan' in output.lower():
                result = {'result': {}}
            else:
                vlans = output.split('-----------------------------------------------------------------------')[1:-1]
                vlans_dict = {}
                for vlan in vlans:
                    vlan_id = re.search(r'\s+VLAN\sID\s+:\s+(\S+)', vlan).groups()[0]
                    vlan_name = re.search(r'\s+Name\s+:\s+(\S+)', vlan).groups()[0]
                    vlans_dict[vlan_id] = vlan_name

                if bool(vlans):
                    if self.vlan_id:
                        result = {'result': {self.vlan_id: vlans_dict[self.vlan_id]}}
                    else:
                        result = {'result': vlans_dict}
                else:
                    vlan_dict = {'result': 'Ip uplink card no any vlan!'}

            self.tn.write("exit\r\n\r\n")

            if protocol == 'http':
                return result
            elif protocol == 'socket':
                self.fiberhomeAN2200_q.put((
                    "update_dslam_command_result",
                    self.dslam_id,
                    "vlan show",
                    result))

        except Exception as ex:
            print ex
            return {'result': 'error: show all vlan get error'}
