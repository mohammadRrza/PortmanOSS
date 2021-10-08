import multiprocessing
from portman_runners import PortInfoSyncTask, DSLAMInitTask, DSLAMBulkCommand,\
        DSLAMPortLineProfileChangeTask, DSLAMPortAdminStatusChangeTask,\
        DSLAMPortStatusInfoTask, DSLAMPortResetAdminStatusInfoTask, DSLAMPortCommandTask
from portman import Portman
import time
import os
from threading import Thread

class Worker(multiprocessing.Process):
    def __init__(self, queue, django_orm_queue, dslam_port_busy_queue=None, request_q=None ,zyxel_q=None ,fiberhomeAN2200_q=None, fiberhomeAN5006_q=None, fiberhomeAN3300_q=None):
        multiprocessing.Process.__init__(self)
        self._dslam_port_busy_queue = dslam_port_busy_queue
        self._queue = queue
        self.request_q = request_q
        self.zyxel_q = zyxel_q
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.fiberhomeAN5006_q = fiberhomeAN5006_q
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.django_orm_queue = django_orm_queue
        self.shutdown = False
        self._loop_interval = 1
        self._portman = Portman(self._queue, self.django_orm_queue, self.request_q, self.zyxel_q, self.fiberhomeAN2200_q, fiberhomeAN5006_q, fiberhomeAN5006_q)

    def __add_dslam_port_busy(self, dslam_id, port_name, command):
        item = str(dslam_id)+'-'+port_name+'-'+command
        self._dslam_port_busy_queue.append(item)

    def __check_dslam_port_busy(self, dslam_id, port_name, command):
        item = str(dslam_id)+'-'+port_name+'-'+command
        return item in self._dslam_port_busy_queue

    def __remove_dslam_port_busy(self, dslam_id, port_name, command):
        item = str(dslam_id)+'-'+port_name+'-'+command
        self._dslam_port_busy_queue.remove(item)

    def shutdown(self):
        self.shutdown = True

    def run(self):
        while not self.shutdown:
            task = self._queue.get()
            if task is None:
                continue
            #check status task
            du = None
            if isinstance(task, DSLAMInitTask):
                thread = Thread(target=self._portman._sync, args=(task,))
                thread.start()
                #self._portman._sync(task)

            elif isinstance(task, PortInfoSyncTask):
                thread = Thread(target=self._portman._resync, args=(task,))
                thread.start()
                #du = self._portman._resync(task)

            elif isinstance(task, DSLAMPortStatusInfoTask): #blocking task
                thread = Thread(target=self._portman.get_status, args=(task,))
                thread.start()
                #self._portman.get_status(task)

            elif isinstance(task, DSLAMPortLineProfileChangeTask): #blocking task
                thread = Thread(target=self._portman._change_lineprofile, args=(task,))
                thread.start()
                #self._portman._change_lineprofile(task)

            elif isinstance(task, DSLAMBulkCommand):
                thread = Thread(target=self._portman._run_bulk_command, args=(task,))
                thread.start()
                #self._portman._run_bulk_command(task)

            elif isinstance(task, DSLAMPortResetAdminStatusInfoTask):
                thread = Thread(target=self._portman._reset_adminstatus, args=(task,))
                thread.start()
                #self._portman._reset_adminstatus(task)

            elif isinstance(task, DSLAMPortAdminStatusChangeTask):
                thread = Thread(target=self._portman._change_adminstatus, args=(task,))
                thread.start()
                #self._portman._change_adminstatus(task)

            elif isinstance(task, DSLAMPortCommandTask):
                busy_key = '-'.join([str(item) for item in list(task.params.values())])
                if not self.__check_dslam_port_busy(task.dslam_data['id'], busy_key, task.command):
                    self.__add_dslam_port_busy(task.dslam_data['id'], busy_key, task.command)
                    thread = Thread(target=self._portman._execute_command, args=(task,))
                    thread.start()
                    #self._portman._execute_command(task)
                    self.__remove_dslam_port_busy(task.dslam_data['id'], busy_key, task.command)
