from vendors.huawei import Huawei
from vendors.zyxel import Zyxel
from vendors.fiberhome import Fiberhome
from portman_factory import PortmanFactory
from django_orm_cursor import Transaction

class PortmanHandler(object):
    def __init__(self, django_orm_queue=None):
        self.__django_orm_queue = django_orm_queue
        self.__portman_factory = PortmanFactory()
        self.__portman_factory.register_type('zyxel', Zyxel)
        self.__portman_factory.register_type('huawei', Huawei)
        self.__portman_factory.register_type('Fiberhome', Fiberhome)
        self.vlans = {}

    def _update_vlan(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        vlans = dslam_class.execute_command(
            task.dslam_data,
            'vlan show'
        )
        if vlans:
            if len(vlans) > 0:
                self.__django_orm_queue.put(("update_vlan", vlans))
        self.vlans = vlans

    def _update_dslamport_mac(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        lst_dslamport_mac = dslam_class.execute_command(
            task.dslam_data,
            'show mac'
        )
        if lst_dslamport_mac:
            if len(lst_dslamport_mac) > 0:
                self.__django_orm_queue.put(("update_dslamport_mac_vlan", task.dslam_data['id'], lst_dslamport_mac, self.vlans))
