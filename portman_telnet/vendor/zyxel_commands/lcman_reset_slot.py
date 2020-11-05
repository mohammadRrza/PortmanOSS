import telnetlib

class LcmanResetSlot(object):
    __slot__ = ('tn', 'slot')
    def __init__(self, tn, params):
        self.tn = tn
        self.slot = params['slot']

    def run_command(self):
        self.tn.write("lcman reset {0}\r\n\r\n".format(self.slot).encode('utf-8'))
        print('*************************************')
        print("reset slot {0}".format(self.slot))
        print('*************************************')
        return "reset slot {0}".format(self.slot)
