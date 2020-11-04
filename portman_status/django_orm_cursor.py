import dj_bridge
from dj_bridge import DSLAM
from dj_bridge import DSLAMStatus
from dj_bridge import DSLAMStatusSnapshot
from dj_bridge import DSLAMEvent

import threading


class DjangoORMCursor(threading.Thread):
    def __init__(self, django_orm_queue):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.django_orm_queue = django_orm_queue
        self.dispatcher = {
                "update_dslam_info": Transaction.update_dslam_info,
                "update_dslam_line_card_status": Transaction.update_dslam_line_card_status,
                "create_dslam_event": Transaction.create_dslam_event
                }

    def run(self):
        while not self.shutdown:
            # first element tell us which call method
            tuple_obj = self.django_orm_queue.get()
            function = self.dispatcher[tuple_obj[0]]
            if len(tuple_obj[1:]) > 1:
                function(*tuple_obj[1:])
            else:
                function(tuple_obj[1])


class Transaction(object):
    @classmethod
    def update_dslam_line_card_status(cls, dslam_id, value):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        dslam_status, created = DSLAMStatus.objects.update_or_create(
                dslam=dslam_obj, defaults={"line_card_temp": value}
            )
        cls._dslam_line_card_status_snapshot(dslam_id, value)


    @classmethod
    def _dslam_line_card_status_snapshot(cls, dslam_id, value):
        snp = DSLAMStatusSnapshot()
        snp.dslam_id = dslam_id
        snp.line_card_temp = value
        snp.save()


    @classmethod
    def update_dslam_info(cls, dslam_id, version, uptime, hostname):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        dslam_obj.uptime = uptime
        dslam_obj.version = version
        dslam_obj.hostname = hostname
        dslam_obj.save()


    @classmethod
    def create_dslam_event(cls, dslam_id, event, message, flag):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        event = DSLAMEvent()
        event.dslam = dslam_obj
        event.type = event
        event.flag = flag
        event.message = message
        event.save()
