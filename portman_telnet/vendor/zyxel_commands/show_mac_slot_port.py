import telnetlib
import time
import re

class ShowMacSlotPort(object):
    __slot__ = ('tn', 'params', 'ports')
    def __init__(self, tn, params=None):
        self.tn = tn
        self.params = params
        self.ports = params.get('ports')

    def run_command(self):
        results = []
        for port in self.ports:
            self.tn.write("show mac {0}-{1}\r\n\r\n".format(port['slot_number'], port['port_number']).encode("utf-8"))
            time.sleep(2)
            self.tn.write("end\r\n")
            result = self.tn.read_until('end')
            com = re.compile(r'(?P<vid>(\s)\d{1,3})(\s)*(?P<mac>([0-9A-F]{2}[:-]){5}([0-9A-F]{2}))(\s)*(?P<port>(\d{1,3})?-(\s)?(\d{1,3})?)',re.MULTILINE | re.I)
            port = com.search(result).group('port').split('-')[1].strip()
            slot = com.search(result).group('port').split('-')[0].strip()
            vid = com.search(result).group('vid')
            mac = com.search(result).group('mac')
            results.append({
                "mac": mac,
                "vid": vid,
                "slot": slot,
                "port": port
                })

        print('***********************')
        print(results)
        print('***********************')
        return {'result': results}
