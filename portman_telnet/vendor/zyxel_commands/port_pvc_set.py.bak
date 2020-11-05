import telnetlib
import time

class PortPvcSet(object):
    __slot__ = ('tn', 'ports', 'vpi', 'vci', 'profile', 'mux', 'vid', 'priority')
    def __init__(self, tn, params):
        self.tn = tn
        self.ports = params.get('ports')
        self.vpi = params.get('vpi', '0')
        self.vci = params.get('vci', '35')
        self.profile = params.get('profile', 'DEFVAL')
        self.mux = params.get('mux', 'llc')
        self.vid = params.get('vid', '1')
        self.priority = params.get('priority', '0')

    def run_command(self):
        for port in self.ports:
            self.tn.write("port pvc set {0}-{1}-{2}/{3} {4} {5} {6} {7}\r\n\r\n".format(
                port['slot_number'], port['port_number'],
                self.vpi,
                self.vci,
                self.profile,
                self.mux,
                self.vid,
                self.priority
            ).encode('utf-8'))
            time.sleep(1)
        print '***********************************************'
        print "port pvc set 0/35 DEFVAL llc  1 0 for {0}".format(self.ports)
        print '***********************************************'
        return dict(result="ports pvc set is done ", ports=self.ports)
