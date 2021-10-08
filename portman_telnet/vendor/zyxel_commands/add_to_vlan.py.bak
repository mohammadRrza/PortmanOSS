import telnetlib
import time

class AddToVlan(object):
    __slot__ = ('tn', 'ports', 'vpi', 'vci', 'profile', 'mux',
            'vid', 'vname', 'priority', )
    def __init__(self, tn, params=None):
        self.tn = tn
        self.ports = params.get('ports')
        self.vpi = params.get('vpi', '0')
        self.vci = params.get('vci', '35')
        self.profile = params.get('profile', 'DEFVAL')
        self.mux = params.get('mux', 'llc')
        self.vid = params.get('vid', '1')
        self.vname = params.get('vname', '1')
        self.priority = params.get('priority', '0')

    def run_command(self):
        self.tn.write("vlan set {0} all fix tag\r\n\r\n".format(
            self.vid,
            ).encode('utf-8'))
        time.sleep(1)
        if self.vname:
            self.tn.write("vlan name {0} {1}\r\n\r\n".format(
                self.vid,
                self.vname
            ).encode('utf-8'))
            time.sleep(1)
        for ports in self.ports:
            self.tn.write("port pvc set {0}-{1}-{2}/{3} {4} {5} {6} {7}\r\n\r\n".format(
                    port['slot_number'], port['port_number'],
                    self.vpi,
                    self.vci,
                    self.profile,
                    self.mux,
                    self.vid,
                    self.priority).encode('utf-8'))
            time.sleep(1)
        self.tn.write("end\r\n")
        result = self.tn.read_until('end')
        if 'example' in result:
            return {"result" : "add to valn {1} give error".format(self.vid), "ports": self.ports}
        print '*********************************'
        print  "{0} added to vlan {1}".format(self.ports, self.vid)
        print '*********************************'
        return dict(result="added to vlan {0}".format(self.vid), ports=self.ports)
