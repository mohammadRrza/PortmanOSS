import dj_bridge
from dj_bridge import DSLAM
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
from vendor.zyxel_telnet import ZyxelTelnet
from vendor.fiberhome2200_telnet import FiberhomeAN2200Telnet
from vendor.fiberhomeAN5006_telnet import FiberhomeAN5006Telnet
from vendor.fiberhomeAN3300_telnet import FiberhomeAN3300Telnet
import socketserver
import threading
import time
from datetime import datetime
from multiprocessing.managers import SyncManager
from multiprocessing import Manager


# Threaded mix-in
class AsyncJSONRPCServer(socketserver.ThreadingMixIn, SimpleJSONRPCServer): pass

class TelnetServer(object):
    def __init__(self, telnet_dict, request_q, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q):
        self.telnet_dict = telnet_dict
        self.shutdown = False
        self.request_q = request_q
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.fiberhomeAN5006_q = fiberhomeAN5006_q
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.zyxel_q = zyxel_q
        check_idle_dslam_telnet = threading.Thread(target=self.check_idle_dslam_telnet)
        check_idle_dslam_telnet.start()
        self.run()

    def run(self):
        while not self.shutdown:
            dslam_id, command, params = self.request_q.get()
            t = threading.Thread(target=self.socket_run_telnet_command, args=(dslam_id, command, params))
            t.start()

    def socket_run_telnet_command(self, dslam_id, command, params):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        if dslam_id not in list(self.telnet_dict.keys()):
            if dslam_obj.id not in list(self.telnet_dict.keys()):
                self.telnet_dict[dslam_obj.id] = (None, None)
            if dslam_obj.dslam_type.id == 1:
                telnet_server = ZyxelTelnet(self.telnet_dict,dslam_obj.get_info(), zyxel_q)
            elif dslam_obj.dslam_type.id == 3:
                telnet_server = FiberhomeAN3300Telnet(self.telnet_dict,dslam_obj.get_info(), self.fiberhomeAN3300_q)
            elif dslam_obj.dslam_type.id == 4:
                telnet_server = FiberhomeAN2200Telnet(self.telnet_dict,dslam_obj.get_info(), self.fiberhomeAN2200_q)
            elif dslam_obj.dslam_type.id == 5:
                telnet_server = FiberhomeAN5006Telnet(self.telnet_dict,dslam_obj.get_info(), self.fiberhomeAN5006_q)
            self.telnet_dict[dslam_obj.id] = (telnet_server, time.time())
        if self.telnet_dict[dslam_id][0]:
            self.telnet_dict[dslam_id][0].run_command(command, params)
        else:
            return {'result': 'result object is None'}

    def check_idle_dslam_telnet(self):
        idle_dslams = []
        while(True):
            diff_time = time.time()
            for key, (telnet_object, created_time) in list(self.telnet_dict.items()):
                if telnet_object:
                    secounds = diff_time - created_time
                    if (secounds // 60) > 10 and telnet_object.tn:
                        idle_dslams.append(key)
                        print(telnet_object)
                        print(dir(telnet_object))
                        telnet_object.tn.close()

            for key in idle_dslams:
                try:
                    del self.telnet_dict[key]
                except Exception as ex:
                    print(ex)

            time.sleep(700)


class PortmanRPC(object):
    def __init__(self, telnet_dict, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q):
        self.telnet_dict = telnet_dict
        self.zyxel_q = zyxel_q
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.fiberhomeAN5006_q = fiberhomeAN5006_q
        self.fiberhomeAN3300_q = fiberhomeAN3300_q

    def telnet_run_command(self, dslam_id, command, params):
        print('----------------------')
        print(dslam_id, command, params)
        print('----------------------')

        if not command:
            return {'result': 'command does not exits'}

        if not dslam_id:
            return {'result': 'dslam_id does not exits'}

        try:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
        except Exception as ex :
            print(ex)
            return {'result': 'Invalid dslam_id'}

        if not dslam_obj.id in list(self.telnet_dict.keys()):
            if dslam_obj.dslam_type.id == 1:
                pass
            elif dslam_obj.dslam_type.id == 4:
                telnet_server = FiberhomeAN2200Telnet(self.telnet_dict, dslam_obj.get_info(), self.fiberhomeAN2200_q)
            elif dslam_obj.dslam_type.id == 3:
                telnet_server = FiberhomeAN3300Telnet(self.telnet_dict, dslam_obj.get_info(), self.fiberhomeAN3300_q)
            elif dslam_obj.dslam_type.id == 5:
                telnet_server = FiberhomeAN5006Telnet(self.telnet_dict, dslam_obj.get_info(), self.fiberhomeAN5006_q)
            self.telnet_dict[dslam_obj.id] = (telnet_server, time.time())
        if self.telnet_dict[dslam_obj.id][0]:
            return self.telnet_dict[dslam_obj.id][0].run_command(command, params, 'http')
        else:
            return {'result': 'result object is None'}


class PortmanRPCStarter(threading.Thread):
    def __init__(self, telnet_dict, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q):
        self.telnet_dict = telnet_dict
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.zyxel_q = zyxel_q
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.fiberhomeAN5006_q = fiberhomeAN5006_q
        threading.Thread.__init__(self)

    def run(self):
        print("Listening on port 7080...")
        server = AsyncJSONRPCServer(('localhost', 7090), SimpleJSONRPCRequestHandler)
        server.register_introspection_functions()
        server.register_multicall_functions()

        server.register_instance(PortmanRPC(self.telnet_dict, self.fiberhomeAN2200_q, self.zyxel_q, self.fiberhomeAN5006_q, self.fiberhomeAN3300_q))
        try:
            print('Use Control-C to exit')
            server.serve_forever()
        except KeyboardInterrupt:
            print('Exiting')

def QueueServerClient(HOST, PORT, AUTHKEY):
    class QueueManager(SyncManager):
        pass

    QueueManager.register('request_q')
    QueueManager.register('fiberhomeAN2200_q')
    QueueManager.register('fiberhomeAN3300_q')
    QueueManager.register('zyxel_q')
    QueueManager.register('fiberhomeAN5006_q')

    manager = QueueManager(address = (HOST, PORT), authkey = AUTHKEY)
    manager.connect() # This starts the connected client
    return manager

def register_client_queue():
    qc = QueueServerClient('localhost', 5011, 'authkey')
    request_q = qc.request_q()
    fiberhomeAN2200_q = qc.fiberhomeAN2200_q()
    zyxel_q = qc.zyxel_q()
    fiberhomeAN5006_q = qc.fiberhomeAN5006_q()
    fiberhomeAN3300_q = qc.fiberhomeAN3300_q()
    return request_q, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q

if __name__ == '__main__':
    request_q, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q = register_client_queue()
    #manager = Manager()
    #telnet_dict = manager.dict()
    telnet_dict = {}
    portman_rpc_starter = PortmanRPCStarter(telnet_dict, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q)
    portman_rpc_starter.start()
    TelnetServer(telnet_dict, request_q, fiberhomeAN2200_q, zyxel_q, fiberhomeAN5006_q, fiberhomeAN3300_q)
