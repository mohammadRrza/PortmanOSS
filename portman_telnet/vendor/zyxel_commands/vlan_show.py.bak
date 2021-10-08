import telnetlib
import time

class VlanShow(object):
    __slots__ = ('tn', 'params', )
    def __init__(self, tn, params=None):
        self.tn = tn
        self.params = params

    def run_command(self):
        self.tn.write(("vlan show\r\n").encode('utf-8'))
        time.sleep(1)
        self.tn.read_until('vid')
        self.tn.write("end\r\n")
        result = self.tn.read_until('end')
        vlans = {}
        for line in result.split('\n')[2:len(result)-1]:
            items = line.split()
            vlans[items[0]] = items[-1]
        print '********************************'
        print vlans
        print '********************************'
        return {"result": vlans}
