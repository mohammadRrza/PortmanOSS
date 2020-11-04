import telnetlib
import time

class Selt(object):
    __slot__ = ('tn', 'ports')
    def init(self, tn, params=None):
        self.tn = tn
        self.ports = params['ports']

    def clear_port_name(self, port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern,port_name,re.M|re.DOTALL)
        return st.group()

    def run_command(self):
        output = ""
        results = []
        prompt = 'command'
        c_n = 1
        for port in self.ports:
            self.tn.write("diagnostic selt test {0}-{1}\n".format(port['slot_number'], port['port_number']).encode('utf-8'))
            time.sleep(1)
        self.tn.write(prompt+str(c_n)+"\n")
        self.tn.read_until(prompt+str(c_n))
        c_n += 1
        time.sleep(10)
        for port in self.ports:
            self.tn.write("diagnostic selt show {0}-{1}\n".format(port['slot_number'], port['port_number']).encode('utf-8'))
            self.tn.write(prompt+str(c_n)+"\n")
            output = self.tn.read_until(prompt+str(c_n)).split('\n')[-2]
            while 'INPROGRESS' in output:
                c_n += 1
                self.tn.write('diagnostic selt show {0}-{1}\n'.format(port['slot_number'], port['port_number']).encode('utf-8'))
                self.tn.write(prompt+str(c_n)+'\n')
                output = self.tn.read_until(prompt+str(c_n)).split('\n')[-2]
                time.sleep(10)
            output = output.replace(self.clear_port_name(output),'')
            result_values = output.split()
            results.append(dict(port={'card': port['slot_number'],'port': port['port_number']}, inprogress=result_values[0]\
                ,cableType=result_values[1], loopEstimateLength=' '.join(result_values[2:])))
        print '**********************************'
        print {'result': results}
        print '**********************************'
        return results
