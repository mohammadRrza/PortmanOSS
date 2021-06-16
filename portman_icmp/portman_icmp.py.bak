import dj_bridge
from dj_bridge import DSLAM
from django_orm_cursor import DjangoORMCursor
from portman_tasks import DSLAMICMPTask
import multiprocessing
from math import ceil
from worker import Worker
import time
import threading
import sys, getopt
import socketserver
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
import queue
from icmp import ICMP

# Threaded mix-in
class AsyncJSONRPCServer(socketserver.ThreadingMixIn,SimpleJSONRPCServer): pass

class PortmanRPC(object):
    icmp_objs = {}
    def run_icmp_command(self, dslam_id, icmp_type, params=None):
        icmp = ICMP()
        socket_id = None
        channel = None
        if not icmp_type:
            return {'result': 'Command does not exits'}
        try:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
        except Exception as ex :
            print(ex)
            return {'result': 'Invalid dslam_id'}

        if icmp_type == 'ping':
            count = params.get('count')
            timeout = params.get('timeout')
            channel = params.get('channel')

            if not count:
                count = 4
            if not timeout:
                timeout = 0.2

            if channel:
                icmp.repeat_ping = True
                socket_id = params.get('socket_id', None)
                PortmanRPC.icmp_objs[socket_id] = icmp
            result = icmp.ping_request(dslam_obj.id, dslam_obj.ip, count, timeout, channel, socket_id)

        elif icmp_type == 'traceroute':
            result = icmp.trace_route_request(dslam_obj.id, dslam_obj.ip)
        return result

    def shutdown_ping_command(self, socket_id):
        PortmanRPC.icmp_objs[socket_id].repeat_ping = False
        del PortmanRPC.icmp_objs[socket_id]
        return 'shutting down socket'

class PortmanRPCStarter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Listening on port 7070...")
        server = AsyncJSONRPCServer(('localhost', 7070), SimpleJSONRPCRequestHandler)
        server.register_introspection_functions()
        server.register_multicall_functions()

        server.register_instance(PortmanRPC())
        try:
            print('Use Control-C to exit')
            server.serve_forever()
        except KeyboardInterrupt:
            print('Exiting')


class Portman_Runner(object):
    def __init__(self, num_workers, ping_timeout, ping_count):
        self.ping_timeout = ping_timeout
        self.ping_count = ping_count

        self.queue = multiprocessing.Queue()

        # Keep All Django ORM Transaction
        self.django_orm_queue = multiprocessing.Queue()

        #worker number
        self.num_workers = num_workers

        self.shutdown = False

        #loop interval for periodic
        self.loop_interval = 1200

        #keep all workers queue for use resync priodic, because we need add tasks at  next time
        self.queues = {}

        self.create_process()

        self.run_service()

        self.exec_django_orm_transaction()

        #run priodic resync
        self.run()

    def run_service(self):
        portman_rpc_starter = PortmanRPCStarter()
        portman_rpc_starter.start()

    def exec_django_orm_transaction(self):
        for item in range(8):
            django_orm_cursor = DjangoORMCursor(self.django_orm_queue)
            django_orm_cursor.start()

    def create_process(self):
        task = None
        for item in range(self.num_workers):
            worker = Worker(self.queue, self.django_orm_queue)
            worker.start()

    def run(self):
        while not self.shutdown:
            self.resync_dslams()
            time.sleep(self.loop_interval)

    def resync_dslams(self):
        print('periodic dslam sync started ... ')
        queryset = DSLAM.objects.all().order_by('status', 'created_at', 'last_sync')
        task = None

        for index, dslam in enumerate(queryset, 1):
            task = DSLAMICMPTask(dslam.get_info(), self.ping_count, self.ping_timeout)
            self.queue.put(task)


if __name__ == '__main__':
    ping_timeout = ''
    ping_count = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:c:", ["timeout=", "count="])
    except getopt.GetoptError:
        print('test.py -c <count> -t <timeout>')
        sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('test.py -c <count> -t <timeout>')
         sys.exit()
      elif opt in ("-c", "--count"):
         ping_count = arg
      elif opt in ("-t", "--timeout"):
         ping_timeout = arg
    num_workers = int(ceil(multiprocessing.cpu_count()*2))
    print('Creating {0} workers'.format(num_workers))
    Portman_Runner(num_workers, ping_timeout, ping_count)
