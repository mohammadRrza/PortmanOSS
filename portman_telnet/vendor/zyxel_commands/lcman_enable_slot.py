import telnetlib

class LcmanEnableSlot(object):
    __slot__ = ('tn', 'slot')
    def __init__(self, tn, params):
        self.tn = tn
        self.slot = params['slot']

    def run_command(self):
        self.tn.write("lcman enable {0}\r\n\r\n".format(self.slot).encode('utf-8'))
        print '************************************'
        print "enable slot {0}".format(self.slot)
        print '************************************'
        return "enable slot {0}".format(self.slot)
