import telnetlib
import re
import time
from .base_command import BaseCommand

class ShowMacSlotPort(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'dslam_id', 'ports', 'fiberhomeAN2200_q')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.port_indexes = params.get('port_indexes')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def run_command(self, protocol):

        self.tn.write("ip\r\n".encode('utf-8'))
        data = self.tn.read_until('>', 5)
        if 'timeout' in data.lower():
            self.tn.close()
            raise ValueError('first, please login session')
        results = []
        for port in self.port_indexes:
            self.tn.write("showmac\r\n".encode('utf-8'))
            self.tn.read_until('>', 5)
            self.tn.write("0-{0}-{1}\r\n".format(port['slot_number'], port['port_number']).encode('utf-8'))
            result = self.tn.read_until('>', 5)
            if 'no up port' in result.lower():
                results.append({'mac': "don't have any mac"})
            else:
                try:
                    mac = re.search(r'(\s)*(?P<mac>([0-9A-F]{2}[:-]){5}([0-9A-F]{2}))(\s)*', result,re.MULTILINE | re.I).groupdict()['mac']
                    results.append({
                        "mac": mac,
                        "slot": port['slot_number'],
                        "port": port['port_number'],
                        "index": port['port_index']
                    })
                except Exception as ex:
                    print(ex)
                    continue

        self.tn.write("exit\r\n".encode('utf-8'))
        results = {"result": results}
        print('===================================')
        print(results)
        print('===================================')

        if protocol == 'http':
            return results
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put(("update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "show mac slot port",
                results))
            self.fiberhomeAN2200_q.put(("partial_update_port_status",
                self.dslam_id,
                "show mac slot port",
                self.port_indexes,
                results
                ))

