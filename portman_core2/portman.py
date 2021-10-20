from vendors.huawei import Huawei
from vendors.zyxel import Zyxel
from vendors.zyxel1248 import Zyxel1248
from vendors.fiberhomeAN2200 import FiberhomeAN2200
from vendors.fiberhomeAN3300 import FiberhomeAN3300
from vendors.fiberhomeAN5006 import FiberhomeAN5006
from switch_vendors.cisco_commands.switch_C2960 import C2960
from router_vendors.mikrotik_commands.RB951Ui2HnD import RB951Ui2HnD
from radio_vendors.wireless_commands.set_radio_geographical_coordinates import SetRadioGeographicalCoordinates

from portman_factory import PortmanFactory
from django_orm_cursor import Transaction
from portman_runners import DSLAMPortCommandTask
from datetime import datetime
from dj_bridge import DSLAM, DSLAMPort, DSLAMType, DSLAMTypeCommand
import time
import os
import sys


class Portman(object):
    def __init__(self, queue=None, django_orm_queue=None, request_q=None, zyxel_q=None, zyxel1248_q=None,
                 fiberhomeAN2200_q=None, fiberhomeAN5006_q=None, fiberhomeAN3300_q=None):
        self.request_q = request_q
        self.zyxel_q = zyxel_q
        self.zyxel1248_q = zyxel1248_q
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.__django_orm_queue = django_orm_queue
        self.__fiberhomeAN5006_q = fiberhomeAN5006_q
        self.__fiberhomeAN3300_q = fiberhomeAN3300_q
        self.__queue = queue
        self.__portman_factory = PortmanFactory()
        # dslams
        self.__portman_factory.register_type('zyxel', Zyxel)
        self.__portman_factory.register_type('zyxel1248', Zyxel1248)
        self.__portman_factory.register_type('huawei', Huawei)
        self.__portman_factory.register_type('fiberhomeAN2200', FiberhomeAN2200)
        self.__portman_factory.register_type('fiberhomeAN3300', FiberhomeAN3300)
        self.__portman_factory.register_type('fiberhomeAN5006', FiberhomeAN5006)

        # switches
        self.__portman_factory.register_type('C2960', C2960)
        self.__portman_factory.register_type('C4500', C2960)
        self.__portman_factory.register_type('4948', C2960)
        self.__portman_factory.register_type('C3850', C2960)
        self.__portman_factory.register_type('C4500x', C2960)
        self.__portman_factory.register_type('ASR1002x', C2960)
        self.__portman_factory.register_type('C3750', C2960)

        # routers
        self.__portman_factory.register_type('RB951', RB951Ui2HnD)
        self.__portman_factory.register_type('CCR1072', RB951Ui2HnD)
        self.__portman_factory.register_type('RB1100AHx2', RB951Ui2HnD)
        self.__portman_factory.register_type('CCR1016', RB951Ui2HnD)
        self.__portman_factory.register_type('hEXRB750', RB951Ui2HnD)
        self.__portman_factory.register_type('RB1200', RB951Ui2HnD)
        self.__portman_factory.register_type('1100AH', RB951Ui2HnD)
        self.__portman_factory.register_type('RB3011UiAS', RB951Ui2HnD)
        self.__portman_factory.register_type('RB2011', RB951Ui2HnD)
        self.__portman_factory.register_type('RB750R2', RB951Ui2HnD)
        self.__portman_factory.register_type('CCR1009', RB951Ui2HnD)
        self.__portman_factory.register_type('750Gr3hEX', RB951Ui2HnD)
        self.__portman_factory.register_type('RB1100Ahx2', RB951Ui2HnD)
        self.__portman_factory.register_type('RB750Gr3', RB951Ui2HnD)
        self.__portman_factory.register_type('RB750R3', RB951Ui2HnD)
        self.__portman_factory.register_type('RB750G', RB951Ui2HnD)
        self.__portman_factory.register_type('RB2011UAS', RB951Ui2HnD)
        self.__portman_factory.register_type('RB1100', RB951Ui2HnD)
        self.__portman_factory.register_type('RB450G', RB951Ui2HnD)
        self.__portman_factory.register_type('C6840x', RB951Ui2HnD)
        self.__portman_factory.register_type('C6816x', RB951Ui2HnD)
        self.__portman_factory.register_type('RB750GL', RB951Ui2HnD)
        self.__portman_factory.register_type('RB750Gr2', RB951Ui2HnD)
        self.__portman_factory.register_type('RB850', RB951Ui2HnD)
        self.__portman_factory.register_type('CCR1100', RB951Ui2HnD)
        self.__portman_factory.register_type('RB1100AH', RB951Ui2HnD)
        self.__portman_factory.register_type('HexRB750', RB951Ui2HnD)
        self.__portman_factory.register_type('RB450', RB951Ui2HnD)
        self.__portman_factory.register_type('CCR1036', RB951Ui2HnD)

        #radios
        self.__portman_factory.register_type('wireless', RB951Ui2HnD)

    def __get_dslam_slot_port(self, slot_port_conditions, dslams_id):
        slot_number_from = slot_port_conditions.get('slot_number_from')
        slot_number_to = slot_port_conditions.get('slot_number_to')
        port_number_from = slot_port_conditions.get('port_number_from')
        port_number_to = slot_port_conditions.get('port_number_to')

        port_number = slot_port_conditions.get('port_number')
        slot_number = slot_port_conditions.get('slot_number')

        line_profile = slot_port_conditions.get('line_profile')
        ports = {}

        if slot_number:
            if port_number:
                for dslam_id in dslams_id:
                    ports[dslam_id] = DSLAMPort.objects. \
                        filter(dslam_id=dslam_id, slot_number=slot_number, port_number=port_number). \
                        values('slot_number', 'port_number', 'port_index')
                return ('port', ports)
            else:
                return ('slot', (slot_number,))

        elif line_profile:
            for dslam_id in dslams_id:
                ports[dslam_id] = DSLAMPort.objects.filter(dslam_id=dslam_id, line_profile=line_profile). \
                    values('slot_number', 'port_number', 'port_index')
            return ('port', ports)

        elif slot_number_from and port_number_from:
            for dslam_id in dslams_id:
                port_objs = DSLAMPort.objects.filter(dslam_id=dslam_id, slot_number__gte=slot_number_from,
                                                     port_number__gte=port_number_from)
                if slot_number_to and port_number_to:
                    port_objs = port_objs.filter(slot_number__lte=slot_number_to, port_number__lte=port_number_to)
                ports[dslam_id] = port_objs.values('slot_number', 'port_number', 'port_index')
            return ('port', ports)

        elif slot_number_from:
            slots = list(DSLAMPort.objects.filter( \
                dslam_id__in=dslams_id, slot_number__gte=slot_number_from \
                ).values_list('slot_number', flat=True).distinct().order_by('slot_number'))

            if slot_number_to:
                slots = [slot for slot in slots if slot <= int(slot_number_to)]
            return ('slot', slots)

    def _run_bulk_command(self, task):
        slot_ports = {}
        commands = task.commands
        telecom_center_id = task.conditions.get('telecom_center_id')
        city_id = task.conditions.get('city_id')
        dslam_type_id = task.conditions.get('dslam_type_id')
        ip_list = task.conditions.get('ip')
        dslam_name = task.conditions.get('dslam_name')
        slot_port_conditions = task.conditions.get('slot_port_conditions')

        if dslam_type_id:
            dslam_type = DSLAMType.objects.get(id=dslam_type_id)
        else:
            return {'result': 'please enter correct dslam_type'}

        dslams = DSLAM.objects.filter(dslam_type=dslam_type)

        if dslam_name:
            dslams = dslams.filter(name__istartswith=dslam_name)

        if telecom_center_id:
            dslams = dslams.filter(telecom_center__id=telecom_center_id)
        elif city_id:
            city = City.objects.get(id=city_id)
            if not city.parent:
                cities_id = City.objects.filter(parent=city_id).values_list('id', flat=True)
                telecom_centers_id = TelecomCenter.objects.filter(city__id__in=cities_id).values_list('id', flat=True)
                dslams = dslams.filter(telecom_center__id__in=telecom_centers_id)

        if ip_list:
            for ip in ip_list:
                dslams = dslams.filter(ip__icontains=ip)
        dslams_info = [dslam.get_info() for dslam in dslams]

        dir_path = os.path.dirname(
            os.path.dirname(os.path.abspath('__file__'))) + '/portman_web/media/bulk_command_result'
        result_filepath = '{0}/{1}.log'.format(dir_path, datetime.now().strftime("%s"))
        success_filepath = '{0}/success-{1}.csv'.format(dir_path, datetime.now().strftime("%s"))
        error_filepath = '{0}/error-{1}.csv'.format(dir_path, datetime.now().strftime("%s"))

        if bool(slot_port_conditions):
            slot_ports = self.__get_dslam_slot_port(slot_port_conditions, list(dslams.values_list('id', flat=True)))
        dslam_class = self.__portman_factory.get_type(dslam_type.name)
        for command in commands:
            command_id = command.get('id')
            command['command_template'] = DSLAMTypeCommand.objects.get(dslam_type=dslam_type,
                                                                       command__id=command_id).command_template
        dslam_class.execute_bulk_command(dslams_info, commands, result_filepath, success_filepath, error_filepath,
                                         slot_ports)

        self.__django_orm_queue.put(("add_dslam_bulk_command_result",
                                     task.title,
                                     success_filepath,
                                     error_filepath,
                                     result_filepath,
                                     task.commands))

    def set_port_index(self, task):
        dslam_id = task.dslam_data['id']
        port_conditions = task.params.get('port_conditions')

        slot_number = port_conditions.get('slot_number')
        port_number = port_conditions.get('port_number')

        slot_number_from = port_conditions.get('slot_number_from')
        slot_number_to = port_conditions.get('slot_number_to')
        port_number_from = port_conditions.get('port_number_from')
        port_number_to = port_conditions.get('port_number_to')

        line_profile = port_conditions.get('lineprofile')

        port_objs = DSLAMPort.objects.filter(dslam__id=dslam_id)

        if None not in (slot_number, port_number):
            port_objs = port_objs.filter(slot_number=slot_number, port_number=port_number)

        if line_profile:
            port_objs = port_objs.filter(line_profile=line_profile)

        if slot_number_from and port_number_from:
            if slot_number_to and port_number_to:
                port_objs = port_objs.filter(
                    slot_number__gte=slot_number_from,
                    port_number__gte=port_number_from).filter(
                    slot_number__lt=slot_number_to,
                    port_number__lt=port_number_to
                )
            else:
                port_objs = port_objs.filter(slot_number__gte=slot_number_from,
                                             port_number__gte=port_number_from)

        task.params['port_indexes'] = list(port_objs.values('port_index', 'slot_number', 'port_number'))

    def _router_execute_command(self, task, is_queue=True, save_result=True):
        router_class = self.__portman_factory.get_type(task.router_data['router_type'])
        print(router_class)
        task_result = router_class.execute_command(
            task.router_data,
            task.command,
            task.params
        )
        router_id = task.router_data['id']
        command = task.command
        if task_result:
            if task_result:
                if not isinstance(task_result, bool):
                    if is_queue:
                        if save_result:
                            return ""
                    else:
                        if save_result:
                            return task_result
                        if task.command == "profile adsl show":
                            return "task.command"

    def _switch_execute_command(self, task, is_queue=True, save_result=True):
        switch_class = self.__portman_factory.get_type(task.switch_data['switch_type'])
        task_result = switch_class.execute_command(
            task.switch_data,
            task.command,
            task.params
        )

        switch_id = task.switch_data['id']
        command = task.command
        if task_result:
            if not isinstance(task_result, bool):
                if is_queue:
                    if save_result:
                        return ""
                else:
                    if save_result:
                        return task_result
                    if task.command == "profile adsl show":
                        return "task.command"

    def _radio_execute_command(self, task, is_queue=True, save_result=True):
        radio_class = self.__portman_factory.get_type(task.radio_data['radio_type'])
        task_result = radio_class.execute_command(
            task.radio_data,
            task.command,
            task.params
        )

        radio_id = task.radio_data['id']
        command = task.command
        if task_result:
            if not isinstance(task_result, bool):
                if is_queue:
                    if save_result:
                        return ""
                else:
                    if save_result:
                        return task_result
                    if task.command == "profile adsl show":
                        return "task.command"

    def _execute_command(self, task, is_queue=True, save_result=True):

        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        print(task.dslam_data)
        print(task.command)
        print(task.params)

        # return  dslam_class
        if task.params.get('port_conditions'):
            self.set_port_index(task)
        task_result = dslam_class.execute_command(
            task.dslam_data,
            task.command,
            task.params
        )

        dslam_id = task.dslam_data['id']
        command = task.command
        print(task_result)
        if task_result:
            if not isinstance(task_result, bool):
                if task.params["type"] == 'dslamport':
                    if is_queue:
                        if save_result:
                            self.__django_orm_queue.put(("update_dslamport_command_result",
                                                         dslam_id,
                                                         task.params['port_indexes'],
                                                         command,
                                                         task_result,
                                                         task.params.get('username'),
                                                         ))

                        if task.command == "change admin status":
                            self.__django_orm_queue.put(("change_port_admin_status",
                                                         dslam_id,
                                                         task.params.get('port_indexes'),
                                                         task.params.get('admin_status')
                                                         ))

                        if task.command == "change lineprofile port":
                            if 'error' not in task_result.get('result'):
                                self.__django_orm_queue.put(("change_port_line_profile",
                                                             dslam_id,
                                                             task.params.get('port_indexes'),
                                                             task.params.get('new_lineprofile')
                                                             ))

                        if task.command == "add to vlan":
                            self.__django_orm_queue.put(("change_port_vlan",
                                                         dslam_id,
                                                         task.params.get('port_indexes'),
                                                         task.params.get('vlan_id')
                                                         ))

                    else:
                        if save_result:
                            Transaction.update_dslamport_command_result(dslam_id,
                                                                        task.params['port_indexes'],
                                                                        command,
                                                                        task_result,
                                                                        task.params.get('username'),
                                                                        )

                        if task.command == "change admin status":
                            Transaction.change_port_admin_status(
                                dslam_id,
                                task.params.get('port_indexes'),
                                task.params.get('admin_status')
                            )

                        elif task.command in ("selt", "show mac slot port"):
                            Transaction.partial_update_port_status(
                                dslam_id,
                                task.command,
                                task.params.get('port_indexes'),
                                task_result
                            )

                        elif task.command == "change lineprofile port":
                            if 'error' not in task_result.get('result'):
                                Transaction.change_port_line_profile(
                                    dslam_id,
                                    task.params.get('port_indexes'),
                                    task.params.get('new_lineprofile')
                                )

                        elif task.command == "add to vlan":
                            Transaction.change_port_vlan(
                                dslam_id,
                                task.params.get('port_indexes'),
                                task.params.get('vlan_id')
                            )

                else:
                    if is_queue:
                        if save_result:
                            self.__django_orm_queue.put(("update_dslam_command_result",
                                                         dslam_id,
                                                         command,
                                                         task_result,
                                                         task.params.get('username'),
                                                         ))
                        if task.command == "profile adsl show":
                            self.__django_orm_queue.put(("update_profile_adsl",
                                                         task_result.get('result')
                                                         ))
                        if task.command == "profile adsl set":
                            self.__django_orm_queue.put(("add_line_profile",
                                                         task.params,
                                                         ))
                        if task.command == "get dslam board":
                            self.__django_orm_queue.put(("update_dslam_board",
                                                         dslam_id,
                                                         task_result
                                                         ))

                    else:
                        if save_result:
                            Transaction.update_dslam_command_result(
                                dslam_id,
                                command,
                                task_result,
                                task.params.get('username'),
                            )

                        if task.command == "profile adsl show":
                            Transaction.update_profile_adsl(
                                task_result.get('result')
                            )
                        if task.command == "profile adsl set":
                            Transaction.add_line_profile(
                                task.params
                            )
        else:
            task_result = {"result": "No results was returned."}
            if save_result:
                if task.params["type"] == 'dslamport':
                    Transaction.update_dslamport_command_result(dslam_id, task.params['port_indexes'], command,
                                                                task_result)
                else:
                    Transaction.update_dslam_command_result(dslam_id, command, task_result)
        return task_result

    def _reset_adminstatus(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        task_result = dslam_class.reset_adminstatus(task.dslam_data, task.port_index)
        return task_result

    def _change_adminstatus(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        task_result = dslam_class.change_port_admin_status(task.dslam_data, task.port_index, task.new_status)
        if task_result:
            self.__django_orm_queue.put(("change_port_admin_status",
                                         task.dslam_data['id'],
                                         task.port_index,
                                         task.new_status
                                         ))
        return task_result

    def _change_lineprofile(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        task_result = dslam_class.change_port_line_profile(task.dslam_data, task.port_index, task.new_lineprofile)
        if task_result:
            self.__django_orm_queue.put(("change_port_line_profile",
                                         task.dslam_data['id'],
                                         task.port_index,
                                         task.new_lineprofile
                                         ))
        return task_result

    def _sync(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        du = None
        try:
            start = time.time()
            if task.dslam_data['dslam_type'] in ('fiberhomeAN2200', 'fiberhomeAN3300'):
                # self.__django_orm_queue.put((
                #    "update_dslam_status",
                #    task.dslam_data['id'],
                #    dict(status="updating")
                #    ))
                ports_status = dslam_class.get_ports_status(task.dslam_data, self.request_q)
                # task = DSLAMPortCommandTask(task.dslam_data, 'profile adsl show', {'is_queue':True, "type": "dslam" })
                # self._execute_command(task, task.params.get('is_queue'), False)
                task2 = DSLAMPortCommandTask(task.dslam_data, 'get dslam board', {'is_queue': True, "type": "dslam"})
                self._execute_command(task2, True, False)
            else:
                self.__django_orm_queue.put((
                    "update_dslam_status",
                    task.dslam_data['id'],
                    dict(status="updating")
                ))
                result = dslam_class.get_port_index_mapping(task.dslam_data)
                if 'dslam_events' in result:
                    dslam_id, event, msg = result['dslam_events']
                    if event == 'dslam_connection_error':
                        self.__django_orm_queue.put((
                            "update_dslam_status",
                            dslam_id,
                            dict(status="error")
                        ))
                    self.__django_orm_queue.put(("dslam_events", dslam_id, event, msg))
                    self.__queue.put(task)
                else:
                    port_index_map = result['port_index_mapping']
                    du = time.time() - start
                    if port_index_map:
                        ports_status = []
                        for slot_number, port_number, port_index, port_name in port_index_map:
                            port_results = dslam_class.get_current_port_status(
                                task.dslam_data, slot_number, port_number, port_index
                            )
                            if len(port_results['port_events']['port_event_items']) > 0:
                                self.__django_orm_queue.put(('port_events', port_results['port_events']))
                            port_status = port_results['port_current_status']
                            port_status['PORT_NAME'] = port_name
                            port_status['PORT_INDEX'] = port_index
                            port_status['SLOT_NUMBER'] = slot_number
                            port_status['PORT_NUMBER'] = port_number
                            ports_status.append(port_status)
                        self.__django_orm_queue.put(('update_port_status', task.dslam_data.get('id'), ports_status))
                    task = DSLAMPortCommandTask(task.dslam_data, 'profile adsl show',
                                                {'is_queue': True, "type": "dslam"})
                    task2 = DSLAMPortCommandTask(task.dslam_data, 'get dslam board',
                                                 {'is_queue': True, "type": "dslam"})
                    self._execute_command(task, task.params.get('is_queue'), False)
                    self._execute_command(task2, task.params.get('is_queue'), False)
                    dslam_uptime, dslam_hostname = dslam_class.get_dslam_info(task.dslam_data)
                    self.__django_orm_queue.put((
                        "update_dslam_status",
                        task.dslam_data['id'],
                        dict(status='ready', uptime=dslam_uptime, hostname=dslam_hostname)
                    ))
        except Exception as e:
            print(('Error on {0} : {1}'.format(task, e)))
            self.__django_orm_queue.put((
                "update_dslam_status",
                task.dslam_data['id'],
                dict(status='error')
            ))
        return du

    def _resync(self, task):
        dslam_class = self.__portman_factory.get_type(task.dslam_data['dslam_type'])
        task.result = []
        start = time.time()
        du = None
        if task.dslam_data['dslam_type'] in ('fiberhomeAN2200', 'fiberhomeAN3300'):
            self.__django_orm_queue.put((
                "update_dslam_status",
                task.dslam_data['id'],
                dict(status="updating")
            ))
            ports_status = dslam_class.get_ports_status(task.dslam_data, self.request_q)
            task = DSLAMPortCommandTask(task.dslam_data, 'profile adsl show', {'is_queue': True, "type": "dslam"})
            self._execute_command(task, task.params.get('is_queue'), False)
            task2 = DSLAMPortCommandTask(task.dslam_data, 'get dslam board', {'is_queue': True, "type": "dslam"})
            self._execute_command(task2, True, False)

            dslam_class.get_port_vpi_vci(task.dslam_data, self.request_q)
        else:
            try:
                if len(task.dslam_port_map) > 0:
                    self.__django_orm_queue.put((
                        "update_dslam_status",
                        task.dslam_data['id'],
                        dict(status="updating")
                    ))
                    ports_status = []
                    for slot_number, port_number, port_index, port_name in task.dslam_port_map:

                        port_results = dslam_class.get_current_port_status(
                            task.dslam_data, slot_number, port_number, port_index
                        )

                        if len(port_results['port_events']['port_event_items']) > 0:
                            self.__django_orm_queue.put(('port_events', port_results['port_events']))

                        port_status = port_results['port_current_status']

                        port_status['PORT_NAME'] = port_name
                        port_status['PORT_INDEX'] = port_index
                        port_status['SLOT_NUMBER'] = slot_number
                        port_status['PORT_NUMBER'] = port_number
                        ports_status.append(port_status)

                    self.__django_orm_queue.put(('update_port_status', task.dslam_data.get('id'), ports_status))
                    task = DSLAMPortCommandTask(task.dslam_data, 'profile adsl show',
                                                {'is_queue': True, "type": "dslam"})
                    task2 = DSLAMPortCommandTask(task.dslam_data, 'get dslam board',
                                                 {'is_queue': True, "type": "dslam"})
                    self._execute_command(task, task.params.get('is_queue'), False)
                    self._execute_command(task2, task.params.get('is_queue'), False)
                    info = dslam_class.get_port_vpi_vci(task.dslam_data)
                    if 'dslam_events' in list(info.keys()):
                        pass
                    elif 'port_vpi_vci' in list(info.keys()):
                        self.__django_orm_queue.put((
                            "update_port_vpi_vci",
                            task.dslam_data['id'],
                            info.get('port_vpi_vci')
                        ))

                dslam_uptime, dslam_hostname = dslam_class.get_dslam_info(task.dslam_data)
                self.__django_orm_queue.put((
                    "update_dslam_status",
                    task.dslam_data['id'],
                    dict(status='ready', uptime=dslam_uptime, hostname=dslam_hostname)
                ))
            except Exception as e:
                print(('Error on {0}-{1} : {2}'.format(port_index, port_name, e)))
                self.__django_orm_queue.put((
                    "update_dslam_status",
                    task.dslam_data['id'],
                    dict(status='error')
                ))
            finally:
                du = time.time() - start
                return du
