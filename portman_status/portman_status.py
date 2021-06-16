from dj_bridge import DSLAM

from django_orm_cursor import DjangoORMCursor

from portman_tasks import DSLAMStatus

import multiprocessing
from math import ceil
import datetime
from worker import Worker
import time
import queue
import socketserver
from portman_vendors import PortmanVendors
import threading
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler


# Threaded mix-in
class AsyncJSONRPCServer(socketserver.ThreadingMixIn, SimpleJSONRPCServer): pass


class PortmanRPC(object):
    def __init__(self, django_orm_queue):
        self.django_orm_queue = django_orm_queue

    def general_update(self, dslam_id):
        try:
            dslam = DSLAM.objects.get(id=dslam_id)
        except Exception as ex:
            return {'result': 'Dslam does not exist'}
        portman_vendors = PortmanVendors(self.django_orm_queue)
        task = DSLAMStatus(dslam.get_info())
        portman_vendors._update_dslam_status(task)
        return {'result': 'DSLAM general update is doing !!!'}


class PortmanRPCStarter(threading.Thread):
    def __init__(self, django_orm_queue):
        threading.Thread.__init__(self)
        self.django_orm_queue = django_orm_queue

    def run(self):
        print("Listening on port 7070...")
        server = AsyncJSONRPCServer(('localhost', 7080), SimpleJSONRPCRequestHandler)
        server.register_introspection_functions()
        server.register_multicall_functions()

        server.register_instance(PortmanRPC(self.django_orm_queue))
        try:
            print('Use Control-C to exit')
            server.serve_forever()
        except KeyboardInterrupt:
            print('Exiting')


class Portman_Runner(object):
    def __init__(self, num_workers):
        self.queue = multiprocessing.Queue()

        # Keep All Django ORM Transaction
        self.django_orm_queue = multiprocessing.Queue()

        # worker number
        self.num_workers = num_workers

        self.shutdown = False

        # loop interval for periodic
        self.loop_interval = 360

        # keep all workers queue for use resync priodic, because we need add tasks at  next time
        self.queues = {}

        self.create_process()

        self.exec_django_orm_transaction()

        self.run_service()

        # run priodic resync
        self.run()

    def run_service(self):
        portman_rpc_starter = PortmanRPCStarter(self.django_orm_queue)
        portman_rpc_starter.start()

    def exec_django_orm_transaction(self):
        for item in range(8):
            django_orm_cursor = DjangoORMCursor(self.django_orm_queue)
            django_orm_cursor.start()

    def create_process(self):
        for item in range(self.num_workers):
            worker = Worker(self.queue, self.django_orm_queue)
            worker.start()

    def run(self):
        while not self.shutdown:
            self.resync_dslams()
            time.sleep(self.loop_interval)

    def resync_dslams(self):
        print('periodic dslam sync started ... ')

        queryset = DSLAM.objects.filter(dslam_type__id=1).order_by('status', 'created_at', 'last_sync')
        task = None

        for index, dslam in enumerate(queryset, 1):
            task = DSLAMStatus(dslam.get_info())
            self.queue.put(task)


if __name__ == '__main__':
    num_workers = int(ceil(multiprocessing.cpu_count() * 2))
    print('Creating {0} workers'.format(num_workers))
    Portman_Runner(num_workers)
