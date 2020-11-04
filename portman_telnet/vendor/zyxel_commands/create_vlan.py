import telnetlib
import time

class CreateVlan(object):
    __slot__ = ('tn', 'vid', 'vname', )
    def __init__(self, tn, params=None):
        self.tn = tn
        self.vid = params.get('vid','1')
        self.vname = params.get('vname',None)

    def run_command(self):
        self.tn.write("vlan set {0} all fix tag\r\n\r\n".format(
            self.vid
        ).encode('utf-8'))
        time.sleep(1)
        if self.vname:
            self.tn.write("vlan name {0} {1}\r\n\r\n".format(
                self.vid,
                self.vname
            ).encode('utf-8'))
            time.sleep(1)
        self.tn.write("end\r\n")
        result = self.tn.read_until('end')
        if 'example' in result:
            print '************************************'
            print "error: {0} vlan created".format(self.vid)
            print '************************************'
            return {"result": "error: {0} vlan created".format(self.vid)}
        print '************************************'
        print "{0} vlan created".format(self.vid)
        print '************************************'
        return {"result": "{0} vlan created".format(self.vid)}
