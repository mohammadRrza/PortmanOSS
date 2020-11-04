import dj_bridge
from dj_bridge import DSLAM
from django_orm_cursor import DjangoORMCursor
from portman_tasks import DSLAMMacTask
import multiprocessing
from math import ceil
from worker import Worker
import time
import threading
import queue

class Portman_Runner(object):
    def __init__(self, num_worker):

        self.queue = multiprocessing.Queue()

        # Keep All Django ORM Transaction
        self.django_orm_queue = multiprocessing.Queue()

        #worker number
        self.num_workers = num_workers

        self.shutdown = False

        #loop interval for periodic
        self.loop_interval = 1800

        #keep all workers queue for use resync priodic, because we need add tasks at  next time
        self.queues = {}

        self.create_process()


        self.exec_django_orm_transaction()

        #run priodic resync
        self.run()

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

        queryset = DSLAM.objects.all().order_by('status', 'created_at', 'last_sync')
        task = None

        for index, dslam in enumerate(queryset, 1):
            if dslam.status == 'error' or dslam.dslam_type.name != 'zyxel':
                continue
            task = DSLAMMacTask(dslam.get_info(), dslam.get_port_index_map())
            self.queue.put(task)


if __name__ == '__main__':
    num_workers = int(ceil(multiprocessing.cpu_count()*2))
    print('Creating {0} workers'.format(num_workers))
    Portman_Runner(num_workers)
