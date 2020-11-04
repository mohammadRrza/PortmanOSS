from vendors.zyxel import Zyxel

from portman_factory import PortmanFactory

import datetime
import time

class PortmanVendors(object):
    def __init__(self, django_orm_queue):
        self.__django_orm_queue = django_orm_queue
        self.__portman_factory = PortmanFactory()
        self.__portman_factory.register_type('zyxel', Zyxel)

    def _update_dslam_status(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        dslam_status_results = dslam_class.get_dslam_status(task.dslam_data)
        if dslam_status_results:

            if dslam_status_results['uptime'] and dslam_status_results['hostname']:
                self.__django_orm_queue.put((
                    "update_dslam_info",
                    task.dslam_data['id'],
                    dslam_status_results['version'],
                    dslam_status_results['uptime']['value'],
                    dslam_status_results['hostname']['value'],
                    ))

            if dslam_status_results['line_card_temp']:
                self.__django_orm_queue.put((
                    "update_dslam_line_card_status",
                    task.dslam_data['id'],
                    dslam_status_results['line_card_temp']['value']))

            try:
                if 'event' in list(dslam_status_results['uptime'].keys()):
                    self.__django_orm_queue.put((
                        "create_dslam_event",
                        task.dslam_data['id'],
                        dslam_status_results['uptime']['event'],
                        dslam_status_results['uptime']['message'],
                        'warning'))
            except Exception as ex:
                print('=>>>>>>>>>', ex)
                print('=>>>>>>>>>', dslam_status_results)

            try:
                if 'event' in list(dslam_status_results['line_card_temp'].keys()):
                    self.__django_orm_queue.put((
                        "create_dslam_event",
                        task.dslam_data['id'],
                        dslam_status_results['line_card_temp']['event'],
                        dslam_status_results['line_card_temp']['message'],
                        'warning'))
            except Exception as ex:
                print('=>>>>>>>>>', ex)
                print('=>>>>>>>>>', dslam_status_results)

            try:
                if 'event' in list(dslam_status_results['hostname'].keys()):
                    self.__django_orm_queue.put((
                        "create_dslam_event",
                        task.dslam_data['id'],
                        dslam_status_results['uptime']['event'],
                        dslam_status_results['uptime']['message'],
                        'warning'))
            except Exception as ex:
                print('=>>>>>>>>>', ex)
                print('=>>>>>>>>>', dslam_status_results)

        return dslam_status_results
