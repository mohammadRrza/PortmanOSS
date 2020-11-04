import dj_bridge
from dj_bridge import DSLAM
from dj_bridge import DSLAMICMP
from dj_bridge import DSLAMICMPSnapshot
from dj_bridge import DSLAMEvent
import threading

class DjangoORMCursor(threading.Thread):
    def __init__(self, django_orm_queue):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.django_orm_queue = django_orm_queue
        self.dispatcher = {
                "update_dslam_icmp": Transaction.update_dslam_icmp,
                "create_dslam_event": Transaction.create_dslam_event
                }

    def run(self):
        while not self.shutdown:
            # first element tell us which call method
            tuple_obj = self.django_orm_queue.get()
            function = self.dispatcher[tuple_obj[0]]
            if len(tuple_obj[1:])>1:
                function(*tuple_obj[1:])
            else:
                function(tuple_obj[1])

class Transaction(object):
    @classmethod
    def update_dslam_icmp(cls, dslam_id, ping_dict_results, trace_route_result):
        try:
            received = ping_dict_results.get('received')
            sent = ping_dict_results.get('sent')
            jitter = ping_dict_results.get('jitter')
            packet_loss = ping_dict_results.get('packet_loss')
            avgping = ping_dict_results.get('avgping')
            minping = ping_dict_results.get('minping')
            maxping = ping_dict_results.get('maxping')
            dslam_obj = DSLAM.objects.get(id=dslam_id)
            dslam_icmp, created = DSLAMICMP.objects.update_or_create(
                dslam=dslam_obj,
                defaults={
                    "avgping": avgping,
                    "jitter": jitter,
                    "maxping": maxping,
                    "minping": minping,
                    "packet_loss": packet_loss,
                    "received": received,
                    "sent": sent,
                    "trace_route": trace_route_result
                }
            )
            if int(packet_loss) > 25:
                dslam_obj.down_seconds = int(dslam_obj.down_seconds) + 1200
                dslam_obj.save()
            cls._dslam_icmp_snapshot(dslam_id, ping_dict_results, trace_route_result)
        except Exception as e:
            print(e)
            print('------------------------------')
            print(dslam_id)
            print(ping_dict_results)
            print(trace_route_result)
            print('------------------------------')

    @classmethod
    def _dslam_icmp_snapshot(cls, dslam_id, ping_dict_results, trace_route_result):
        snp = DSLAMICMPSnapshot()
        snp.dslam_id = dslam_id
        snp.avgping = ping_dict_results.get('avgping')
        snp.jitter = ping_dict_results.get('jitter')
        snp.maxping = ping_dict_results.get('maxping')
        snp.minping = ping_dict_results.get('minping')
        snp.received = ping_dict_results.get('received')
        snp.packet_loss = ping_dict_results.get('packet_loss')
        snp.sent = ping_dict_results.get('sent')
        snp.trace_route = trace_route_result
        snp.save()

    @classmethod
    def create_dslam_event(cls, dslam_id, event, message, flag):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        event = DSLAMEvent()
        event.dslam = dslam_obj
        event.type = event
        event.flag = flag
        event.message = message
        event.save()
