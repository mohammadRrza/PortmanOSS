import multiprocessing
from portman_tasks import DSLAMStatus
from portman_vendors import PortmanVendors

class Worker(multiprocessing.Process):
    def __init__(self, tasks, django_orm_queue):
        multiprocessing.Process.__init__(self)
        self._tasks = tasks
        self.django_orm_queue = django_orm_queue
        self.shutdown = False
        self._loop_interval = 1
        self.lock = multiprocessing.Lock()

        self._portman_vendors = PortmanVendors(self.django_orm_queue)

    def shutdown(self):
        self.shutdown = True

    def run(self):
        while not self.shutdown:
            task = self._tasks.get()
            if task is None:
                continue
            #check status task
            du = None
            if isinstance(task, DSLAMStatus):
                self._portman_vendors._update_dslam_status(task)
