import dj_bridge
from dj_bridge import DSLAM
from dj_bridge import DSLAMPort
from dj_bridge import DSLAMPortMac
from dj_bridge import DSLAMPortVlan
from dj_bridge import Vlan
import threading

class DjangoORMCursor(threading.Thread):
    def __init__(self, django_orm_queue):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.django_orm_queue = django_orm_queue
        self.dispatcher = {
                "update_dslamport_mac_vlan": Transaction.update_dslamport_mac_vlan,
                "update_vlan": Transaction.update_vlan,
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
    def update_dslamport_mac_vlan(cls, dslam_id, lst_dslamport_mac, vlans):
        try:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
            for vlan_id, mac, card, port in lst_dslamport_mac:
                vlan_name = vlans.get(vlan_id,vlan_id)
                vlan_obj = Vlan.objects.get(vlan_id=vlan_id)
                port_obj = DSLAMPort.objects.get(dslam=dslam_obj, slot_number=card, port_number=port)
                dslamport_mac_obj, created_port_mac_obj = DSLAMPortMac.objects.get_or_create(
                            port=port_obj,
                            mac_address=mac
                            )
                dslamport_vlan_obj, created_port_vlan_obj = DSLAMPortVlan.objects.get_or_create(
                            port=port_obj,
                            vlan=vlan_obj
                            )
        except Exception as e:
            print(e)
            print('------------------------------')
            print(vlan_id, vlan_name)
            print(dslam_obj)
            print(lst_dslamport_mac)
            print('------------------------------')


    @classmethod
    def update_vlan(cls, vlans):
        for vlan_id,vlan_name in vlans.items():
            try:
                Vlan.objects.get_or_create(vlan_id=vlan_id, vlan_name=vlan_name)
            except Exception as ex:
                print(ex)
