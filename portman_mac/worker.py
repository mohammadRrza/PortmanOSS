import multiprocessing
from portman_tasks import DSLAMMacTask
from portman import PortmanHandler

class Worker(multiprocessing.Process):
    def __init__(self, tasks, django_orm_queue):
        multiprocessing.Process.__init__(self)
        self._tasks = tasks
        self.django_orm_queue = django_orm_queue
        self.shutdown = False
        self._portman_handler = PortmanHandler(self.django_orm_queue)

    def shutdown(self):
        self.shutdown = True

    def run(self):
        while not self.shutdown:
            task = self._tasks.get()
            if task is None:
                continue
            #check status task
            du = None
            if isinstance(task, DSLAMMacTask):
                self._portman_handler._update_vlan(task)
                self._portman_handler._update_dslamport_mac(task)
