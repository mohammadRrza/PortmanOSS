import telnetlib
import time

class PortEnable(object):
    __slot__ = ('tn', 'ports')
    def __init__(self, tn, params):
        self.tn = tn
        self.ports = params.get('ports')

    def run_command(self):
        for port in self.ports:
            self.tn.write("port enable {0}-{1}\r\n\r\n".format(port['slot_number'], port['port_number']).encode('utf-8'))
            time.sleep(1)
        print '******************************************'
        print "port enable {0}".format(self.ports)
        print '******************************************'
        return dict(result="ports was enabled", ports=self.ports)
