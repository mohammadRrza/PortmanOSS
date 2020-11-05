import telnetlib
import time

class LcmanShow(object):
    __slot__ = ('tn', )
    def __init__(self, tn, params=None):
        self.tn = tn

    def run_command(self):
        self.tn.write("lcman show\r\n".encode('utf-8'))
        self.tn.read_until("lcman show", 1000)
        time.sleep(1)
        self.tn.write("end\r\n")
        result = self.tn.read_until("end").split('\r\n')
        result = result[1:len(result)-2]
        result = '\n'.join(result)
        print('**************************************')
        print(result)
        print('**************************************')
        return {"result": result}
