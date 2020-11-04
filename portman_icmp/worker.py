import multiprocessing
from portman_tasks import DSLAMICMPTask
from icmp import ICMP

class Worker(multiprocessing.Process):
    def __init__(self, tasks, django_orm_queue):
        multiprocessing.Process.__init__(self)
        self._tasks = tasks
        self.django_orm_queue = django_orm_queue
        self.shutdown = False
        self._icmp = ICMP(self.django_orm_queue)

    def shutdown(self):
        self.shutdown = True

    def run(self):
        while not self.shutdown:
            task = self._tasks.get()
            if task is None:
                continue
            #check status task
            du = None
            if isinstance(task, DSLAMICMPTask):
                self._icmp._update_dslam_icmp(task)
