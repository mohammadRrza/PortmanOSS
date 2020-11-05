import telnetlib
import time

class LcmanShowSlot(object):
    __slot__ = ('tn', 'slot', )
    def __init__(self, tn, params):
        self.tn = tn
        self.slot = params['slot']

    def run_command(self):
        self.tn.write("lcman show {0}\r\n\r\n".format(self.slot).encode('utf-8'))
        time.sleep(1)
        self.tn.write("end\r\n")
        result = self.tn.read_until('end')
        start_point = result.find('slot')
        end_point = result.rfind('\r\n\r\n')
        result = result[start_point:end_point]
        print('********************************')
        print(result)
        print('********************************')
        return {"result": result}
