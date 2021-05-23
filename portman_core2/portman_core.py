import dj_bridge
import logging
from dj_bridge import DSLAM, Router, Switch
from dj_bridge import DSLAMType
from dj_bridge import TelecomCenter
from dj_bridge import City
from dj_bridge import DSLAMPort
from dj_bridge import DSLAMPortSnapshot

from django_orm_cursor import DjangoORMCursor

from portman_runners import PortInfoSyncTask, DSLAMInitTask, DSLAMBulkCommand, \
    DSLAMPortLineProfileChangeTask, DSLAMPortStatusInfoTask, \
    DSLAMPortResetAdminStatusInfoTask, DSLAMPortAdminStatusChangeTask, DSLAMPortCommandTask, \
    RouterCommandTask,SwitchCommandTask

import multiprocessing
from multiprocessing import Manager
from multiprocessing.managers import SyncManager

import threading
from math import ceil
from worker import Worker
from datetime import datetime
import os
import signal
from portman import Portman
import time
import socketserver
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
from port_status_monitoring import PortStatusMonitoring
from threading import Thread
from tornado.ioloop import IOLoop


# Threaded mix-in
class AsyncJSONRPCServer(socketserver.ThreadingMixIn, SimpleJSONRPCServer): pass


class PortmanRPC(object):
    """
    To create a signaling interface between interface(front-end) and backend
    for coordination and execution of tasks
    """
    port_monitoring = {}

    def __init__(self, portman_runner):
        self.task_index = 0
        self.portman_runner = portman_runner
        self.portman = Portman(django_orm_queue=self.portman_runner.django_orm_queue,
                               request_q=self.portman_runner.request_q, zyxel_q=self.portman_runner.zyxel_q,
                               zyxel1248_q=self.portman_runner.zyxel1248_q,
                               fiberhomeAN2200_q=self.portman_runner.fiberhomeAN2200_q,
                               fiberhomeAN5006_q=self.portman_runner.fiberhomeAN5006_q,
                               fiberhomeAN3300_q=self.portman_runner.fiberhomeAN3300_q)

    def shutdown_portman(self):
        self.portman_runner.shutdown_portman()
        return 'Shutting Down ...'

    def get_port_status(self, dslam_id, params):
        psm = PortStatusMonitoring(django_orm_queue=self.portman_runner.django_orm_queue)
        # params = {'port': port ,'channel': 'port_status', 'socket_id': socket_id}
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        psm.get_port_status(dslam_obj.get_info(), params)
        PortmanRPC.port_monitoring[params.get('socket_id')] = psm

    def shutdown_port_status_periodic(self, socket_id):
        PortmanRPC.port_monitoring[socket_id].repeat_port_status = False
        del PortmanRPC.port_monitoring[socket_id]
        return 'shutting down {0}'.format(socket_id)

    def bulk_commands(self, title, commands, conditions):
        print('-------------------------------------------')
        print((title, commands, conditions))
        print('-------------------------------------------')
        task = DSLAMBulkCommand(title, commands, conditions)
        self.portman_runner.add_to_service_queue(task)
        return 'wait for a few moments'

    def scan_dslamport(self, dslam_id):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        '''task = DSLAMInitTask(dslam_obj.get_info())
        thread = Thread(target=self.portman._sync, args=(task,))
        thread.start()'''
        if dslam_obj.status == 'ready':
            task = PortInfoSyncTask(dslam_obj.get_info(), dslam_obj.get_port_index_map())
        elif dslam_obj.status == 'new' or dslam_obj.status == 'error':
            task = DSLAMInitTask(dslam_obj.get_info())
        elif dslam_obj.status == 'updating':
            return 'dslam is updating'
        self.portman_runner.add_to_service_queue(task)

        return 'done'

    def get_port_info(self, dslam_id, port_id):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        port_obj = DSLAMPort.objects.get(id=port_id)
        task = DSLAMPortStatusInfoTask(
            dslam_obj.get_info(), port_obj.port_index
        )
        self.portman_runner.add_to_service_queue(task)

    def change_port_admin_status(self, dslam_id, port_id, new_status):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        port_obj = DSLAMPort.objects.get(id=port_id)
        task = DSLAMPortAdminStatusChangeTask(
            dslam_obj.get_info(), port_obj.port_index, new_status
        )
        self.portman_runner.add_to_service_queue(task)

    def change_port_line_profile(self, dslam_id, port_id, new_line_profile):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        port_obj = DSLAMPort.objects.get(id=port_id)
        task = DSLAMPortLineProfileChangeTask(
            dslam_obj.get_info(), port_obj.port_index, new_line_profile
        )
        self.portman_runner.add_to_service_queue(task)

    def reset_admin_status(self, dslam_id, port_id):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        port_obj = DSLAMPort.objects.get(id=port_id)
        if port_obj.admin_status == 'UNLOCK':
            task = DSLAMPortResetAdminStatusInfoTask(
                dslam_obj.get_info(), port_obj.port_index
            )
            self.portman_runner.add_to_service_queue(task)
        else:
            return 'Operation Not Permitted'

    # execute command
    def add_command(self, dslam_id, command, params):
        logging.basicConfig(filename='example.log', level=logging.DEBUG)
        logging.info('AddCommand')
        print('------------------------')
        print((dslam_id, command, params))
        print('------------------------')
        busy_key = '-'.join([str(item) for item in list(params.values())])

        if self.portman_runner.check_dslam_port_busy(dslam_id, busy_key, command):
            print('DSLAM Busy Please Run After 15 Secounds')
            return 'DSLAM Busy Please Run After 15 Secounds'
        else:
            dslam = DSLAM.objects.get(id=dslam_id)
            task = DSLAMPortCommandTask(dslam.get_info(), command, params)
            is_queue = params.get('is_queue')
            if is_queue == False:
                return self.portman._execute_command(task, is_queue)
            else:
                self.portman_runner.add_to_service_queue(task)
                return 'Run Command (Wait for 40 Secounds)'

    def router_run_command(self, router_id, command, params):
        router = Router.objects.get(id=router_id)
        task = RouterCommandTask(router.get_info(), command, params)
        is_queue = params.get('is_queue')
        if (is_queue == False):
            return self.portman._router_execute_command(task, is_queue)

    def switch_run_command(self, switch_id, command, params):
        switch = Switch.objects.get(id=switch_id)
        task = SwitchCommandTask(switch.get_info(), command, params)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(params)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        is_queue = params.get('is_queue')
        if (is_queue == False):
            return self.portman._switch_execute_command(task, is_queue)

class PortmanRPCStarter(threading.Thread):
    def __init__(self, portman_runner):
        threading.Thread.__init__(self)
        self.portman_runner = portman_runner

    def run(self):
        while self.portman_runner.service_queue is None:
            pass

        print("Listening on port 7060...")
        # Instantiate and bind to localhost:8080
        server = AsyncJSONRPCServer(('localhost', 7060), SimpleJSONRPCRequestHandler)
        server.register_introspection_functions()
        server.register_multicall_functions()

        server.register_instance(PortmanRPC(self.portman_runner))
        try:
            print('Use Control-C to exit')
            server.serve_forever()
        except KeyboardInterrupt:
            print('Exiting')


class Portman_Runner(object):
    def __init__(self, num_workers):

        # Keep All Django ORM Transaction
        self.django_orm_queue = multiprocessing.Queue()
        self.django_orm_queue_isnew = multiprocessing.Queue()

        # Keep All Django ORM Transaction
        self.service_django_orm_queue = multiprocessing.Queue()

        # worker number
        self.num_workers = num_workers

        self.shutdown = False

        # use for check dslam port busy when we want run command on it
        manager = Manager()
        self.dslam_port_busy_queue = manager.list()

        # loop interval for periodic
        self.loop_interval = 86400
        # self.loop_interval = 1800

        # user for portman service,this queue asign to  last worker queue for use add task
        self.service_queue = None

        # this queue that dslam's time is less than 500
        self.queue = multiprocessing.Queue()

        # this queue that dslam's time is more than 500
        self.queue_big_task = multiprocessing.Queue()

        # this queue for new process new dslam
        self.queue_isnew = multiprocessing.Queue()

        self.request_q = None
        self.fiberhomeAN2200_q = None
        self.zyxel_q = None
        self.zyxel1248_q = None
        self.fiberhomeAN5006_q = None
        self.fiberhomeAN3300_q = None

        # register queue for communicate between portman_core and portman_telnet
        t = Thread(target=self.register_server_queue)
        t.start()

        while (self.fiberhomeAN2200_q is None or \
               self.zyxel_q is None or \
               self.request_q is None or \
               self.fiberhomeAN5006_q is None or self.fiberhomeAN3300_q is None):
            pass

        self.create_process()

        self.run_service()

        self.exec_django_orm_transaction()

        # run priodic resync
        self.run()

    def create_queue_server(self, HOST, PORT, AUTHKEY):
        request_q = multiprocessing.Queue()
        fiberhomeAN2200_q = multiprocessing.Queue()
        zyxel_q = multiprocessing.Queue()
        fiberhomeAN5006_q = multiprocessing.Queue()
        fiberhomeAN3300_q = multiprocessing.Queue()

        class QueueManager(SyncManager):
            pass

        QueueManager.register('request_q', callable=lambda: request_q)
        QueueManager.register('fiberhomeAN2200_q', callable=lambda: fiberhomeAN2200_q)
        QueueManager.register('fiberhomeAN5006_q', callable=lambda: fiberhomeAN5006_q)
        QueueManager.register('fiberhomeAN3300_q', callable=lambda: fiberhomeAN3300_q)
        QueueManager.register('zyxel_q', callable=lambda: zyxel_q)
        manager = QueueManager(address=(HOST, PORT), authkey=AUTHKEY)
        manager.start()  # This actually starts the server
        return manager

    def register_client_queue(self, HOST, PORT, AUTHKEY):
        class QueueManager(SyncManager):
            pass

        QueueManager.register('request_q')
        QueueManager.register('fiberhomeAN2200_q')
        QueueManager.register('zyxel_q')
        QueueManager.register('fiberhomeAN5006_q')
        QueueManager.register('fiberhomeAN3300_q')

        manager = QueueManager(address=(HOST, PORT), authkey=AUTHKEY)
        manager.connect()  # This starts the connected client

        # create three connected managers
        self.request_q = manager.request_q()
        self.fiberhomeAN2200_q = manager.fiberhomeAN2200_q()
        self.fiberhomeAN5006_q = manager.fiberhomeAN5006_q()
        self.fiberhomeAN3300_q = manager.fiberhomeAN3300_q()
        self.zyxel_q = manager.zyxel_q()
        IOLoop.current().start()

    def register_server_queue(self):
        # Start three queue servers
        HOST = 'localhost'
        PORT = 5011
        AUTHKEY = 'authkey'
        qm0 = self.create_queue_server(HOST, PORT, AUTHKEY)
        self.register_client_queue(HOST, PORT, AUTHKEY)

    def run_service(self):
        portman_rpc_starter = PortmanRPCStarter(self)
        portman_rpc_starter.start()

    def add_to_service_queue(self, task):
        self.service_queue.put(task)

    def shutdown_portman(self):
        os.killpg(os.getpid(), signal.SIGTERM)
        self.shutdown = True

    def add_dslam_port_busy(self, dslam_id, busy_key, command):
        item = str(dslam_id) + '-' + busy_key + '-' + command
        self.dslam_port_busy_queue.append(item)

    def check_dslam_port_busy(self, dslam_id, busy_key, command):
        item = str(dslam_id) + '-' + busy_key + '-' + command
        return item in self.dslam_port_busy_queue

    def remove_dslam_port_busy(self, dslam_id, busy_key, command):
        item = str(dslam_id) + '-' + busy_key + '-' + command
        self.dslam_port_busy_queue.remove(item)

    def exec_django_orm_transaction(self):
        for item in range(self.num_workers * 2):
            django_orm_cursor = DjangoORMCursor(self.django_orm_queue)
            django_orm_cursor.start()

        for item in range(self.num_workers * 2):
            django_orm_cursor = DjangoORMCursor(self.django_orm_queue_isnew)
            django_orm_cursor.start()

        for item in range(int(self.num_workers / 2)):
            django_orm_cursor_fiberhomeAN2200_q = DjangoORMCursor(self.fiberhomeAN2200_q)
            django_orm_cursor_fiberhomeAN2200_q.start()

        for item in range(int(self.num_workers / 2)):
            django_orm_cursor_fiberhomeAN5006_q = DjangoORMCursor(self.fiberhomeAN5006_q)
            django_orm_cursor_fiberhomeAN5006_q.start()

        for item in range(int(self.num_workers / 2)):
            django_orm_cursor_fiberhomeAN3300_q = DjangoORMCursor(self.fiberhomeAN3300_q)
            django_orm_cursor_fiberhomeAN3300_q.start()

        # start thread for run task of service queue
        django_orm_cursor = DjangoORMCursor(self.service_django_orm_queue)
        django_orm_cursor.start()

    def create_process(self):

        # run worker that dslam's time is less than 500
        for item in range(1, self.num_workers * 2):
            worker = Worker(queue=self.queue, django_orm_queue=self.django_orm_queue, \
                            request_q=self.request_q, zyxel_q=self.zyxel_q, fiberhomeAN2200_q=self.fiberhomeAN2200_q,
                            fiberhomeAN5006_q=self.fiberhomeAN5006_q, fiberhomeAN3300_q=self.fiberhomeAN3300_q)
            worker.start()

        # run worker that dslam's time is more than 500
        for item in range(1, self.num_workers * 4):
            worker = Worker(queue=self.queue_big_task, django_orm_queue=self.django_orm_queue, request_q=self.request_q,
                            zyxel_q=self.zyxel_q, fiberhomeAN2200_q=self.fiberhomeAN2200_q,
                            fiberhomeAN5006_q=self.fiberhomeAN5006_q, fiberhomeAN3300_q=self.fiberhomeAN3300_q)
            worker.start()
        # run worker for dslam new
        for item in range(int(self.num_workers / 4)):
            worker = Worker(queue=self.queue_isnew, django_orm_queue=self.django_orm_queue_isnew,
                            request_q=self.request_q, zyxel_q=self.zyxel_q, fiberhomeAN2200_q=self.fiberhomeAN2200_q,
                            fiberhomeAN5006_q=self.fiberhomeAN5006_q, fiberhomeAN3300_q=self.fiberhomeAN3300_q)
            worker.start()

        # used for portman service job
        self.service_queue = multiprocessing.Queue()
        worker = Worker(dslam_port_busy_queue=self.dslam_port_busy_queue, queue=self.service_queue,
                        django_orm_queue=self.service_django_orm_queue,
                        request_q=self.request_q, zyxel_q=self.zyxel_q, fiberhomeAN2200_q=self.fiberhomeAN2200_q,
                        fiberhomeAN5006_q=self.fiberhomeAN5006_q, fiberhomeAN3300_q=self.fiberhomeAN3300_q)
        worker.start()

    def run(self):
        while not self.shutdown:
            self.resync_dslams()
            time.sleep(self.loop_interval)

    def resync_dslams(self):
        print('periodic dslam sync started ... ')

        queryset = DSLAM.objects.all().order_by('last_sync_duration', 'created_at', 'last_sync')
        task = None
        for index, dslam in enumerate(queryset, 1):

            if dslam.dslam_type.id not in (1, 2, 3, 5) or dslam.status == 'error':
                # if dslam.id not in (399,818,921,783,785,168,870,781,288,267,976,182,678,674,796,677,711,977,903,
                # 624,721,714,895,713,549,722,234,640,163,806,220,951,231,378,247,236,863,893,672,728,716,892,222,
                # 808,437,891,811,630,170,710,185,207,171,864,202,204,573,166,621,814,809,381,397,454,213,289,453,
                # 902,380,169,188,377,918,736,294,529,805,987,919,628,225,162,206,191,208,192,198,210,183,367,491,
                # 313,315,983,981,639,949,984,508,487,954,901,898,894,329,971,1086,365,366,665,675,725,318,189,719,
                # 922,812,249,670,379,593,252,862,681,667,493,816,673,224,400,712,490,500,717,985,221,295,952,314,
                # 900) or dslam.status == 'error': if dslam.id not in (399,) or dslam.status == 'error':
                continue
            if dslam.status == 'error':
                task = DSLAMInitTask(dslam.get_info())
                if dslam.last_sync_duration < 500:
                    self.queue.put(task)
                else:
                    self.queue_big_task.put(task)
            elif dslam.status == 'new':
                task = DSLAMInitTask(dslam.get_info())
                self.queue_isnew.put(task)
            elif dslam.status == 'ready':
                task = PortInfoSyncTask(dslam.get_info(), dslam.get_port_index_map())
                if dslam.last_sync_duration < 500:
                    self.queue.put(task)
                else:
                    self.queue_big_task.put(task)
            else:
                continue


if __name__ == '__main__':
    num_workers = int(ceil(multiprocessing.cpu_count() * 4))
    print(('Creating {0} workers'.format(num_workers)))
    Portman_Runner(num_workers)
