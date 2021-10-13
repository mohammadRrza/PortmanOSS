from vendors.huawei import Huawei
from vendors.zyxel import Zyxel
from vendors.fiberhomeAN2200 import FiberhomeAN2200
from vendors.fiberhomeAN3300 import FiberhomeAN3300
from vendors.fiberhomeAN5006 import FiberhomeAN5006
from portman_factory import PortmanFactory
import time
from datetime import datetime
import redis
import json
from threading import Thread

redis_conn = redis.Redis()

class PortStatusMonitoring(object):
    def __init__(self, queue=None, django_orm_queue=None):
        self.__portman_factory = PortmanFactory()
        self.__portman_factory.register_type('zyxel', Zyxel)
        self.__portman_factory.register_type('huawei', Huawei)
        self.__portman_factory.register_type('fiberhomeAN2200', FiberhomeAN2200)
        self.__portman_factory.register_type('fiberhomeAN3300', FiberhomeAN3300)
        self.__portman_factory.register_type('fiberhomeAN5006', FiberhomeAN5006)
        self.redis = redis_conn
        self.repeat_port_status = True
        self.last_incomming_traffic_average_rate = None
        self.last_incomming_traffic = None
        self.last_outgoing_traffic_average_rate = None
        self.last_outgoing_traffic = None
        self.django_orm_queue = django_orm_queue

    def get_port_status(self, dslam_data, params):
        port = params.get('port')
        if port:
            port_index = port.get('port_index')
            port_number = port.get('port_number')
            slot_number = port.get('slot_number')
        socket_id = params.get('socket_id')
        channel = params.get('channel')
        thread = Thread(target=self.get_port_status_periodic, args=(dslam_data, slot_number, port_number, port_index, channel, socket_id))
        thread.start()

    def get_port_status_periodic(self, dslam_data, slot_number, port_number, port_index, channel, socket_id):
        dslam_class = self.__portman_factory.get_type(dslam_data['dslam_type'])
        while(self.repeat_port_status):
            start_time = time.time()
            port_results = dslam_class.get_current_port_status(
                dslam_data, slot_number, port_number, port_index
            )
            total_seconds = int(time.time() - start_time) % 60
            port_status = port_results['port_current_status']
            print(port_status)

            self.django_orm_queue.put(("update_port_status", dslam_data.get('id'), [{"PORT_INDEX": port_index, "PORT_OPER_STATUS": port_status.get('PORT_OPER_STATUS')}]))

            if len(port_results['port_events']['port_event_items']) > 0:
                port_results['port_events']['socket_id'] = socket_id
                port_results['port_events']['time'] = datetime.now().strftime("%H:%M:%S")
                self.redis.publish(channel, json.dumps(port_results['port_events']))
            else:
                port_status['PORT_INDEX'] = port_index
                port_status['SLOT_NUMBER'] = slot_number
                port_status['PORT_NUMBER'] = port_number
                port_status['socket_id'] = socket_id
                port_status['time'] = datetime.now().strftime("%H:%M:%S")
                if not self.last_outgoing_traffic:
                    self.last_outgoing_traffic_average_rate = 0
                    self.last_incomming_traffic_average_rate = 0
                else:
                    self.last_incomming_traffic_average_rate = ((int(port_status['INCOMING_TRAFFIC']) - self.last_incomming_traffic) / (3 + total_seconds) / 1024)
                    self.last_outgoing_traffic_average_rate = ((int(port_status['OUTGOING_TRAFFIC']) - self.last_outgoing_traffic) / (3 + total_seconds) / 1024)

                port_status['INCOMING_TRAFFIC_AVERAGE_RATE'] = self.last_incomming_traffic_average_rate
                port_status['OUTGOING_TRAFFIC_AVERAGE_RATE'] = self.last_outgoing_traffic_average_rate
                self.redis.publish(channel, json.dumps(port_status))
                if 'INCOMING_TRAFFIC' in list(port_status.keys()):
                    self.last_incomming_traffic = int(port_status['INCOMING_TRAFFIC'])
                    self.last_outgoing_traffic = int(port_status['OUTGOING_TRAFFIC'])
                if not dslam_data['dslam_type'] in ('fiberhomeAN2200', 'fiberhomeAN3300'):
                    time.sleep(3)
        print(('shutdown socket_id: ', socket_id))
