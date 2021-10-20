import dj_bridge
from dj_bridge import DSLAM, DSLAMPort, DSLAMPortSnapshot, LineProfile, DSLAMEvent, DSLAMBoard,\
    DSLAMPortEvent, Command, PortCommand, DSLAMCommand, DSLAMBulkCommandResult, DSLAMPortVlan, Vlan, DSLAMPortMac, LineProfileExtraSettings

import time
import datetime
import threading
import queue
from django.core.files import File
from os.path import basename
import os
import sys
import traceback


class DjangoORMCursor(threading.Thread):
    def __init__(self, django_orm_queue):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.django_orm_queue = django_orm_queue
        self.dispatcher = {
            "update_dslam_status": Transaction.update_dslam_status,
            "change_port_admin_status": Transaction.change_port_admin_status,
            "change_port_line_profile": Transaction.change_port_line_profile,
            "dslam_events": Transaction.dslam_events,
            "port_events": Transaction.port_events,
            "update_port_status": Transaction.update_port_status,
            "update_dslamport_command_result": Transaction.update_dslamport_command_result,
            "update_dslam_command_result": Transaction.update_dslam_command_result,
            "add_dslam_bulk_command_result": Transaction.add_dslam_bulk_command_result,
            "update_profile_adsl": Transaction.update_profile_adsl,
            "change_port_vlan": Transaction.change_port_vlan,
            "partial_update_port_status": Transaction.partial_update_port_status,
            "update_dslam_board": Transaction.update_dslam_board,
            "update_port_vpi_vci": Transaction.update_port_vpi_vci
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
    def dslam_events(cls, dslam_id, event, msg):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        dslam_event = DSLAMEvent(
            dslam = dslam_obj,
            type = event,
            message = msg)
        dslam_event.save()


    @classmethod
    def port_events(cls, port_events):
        dslam_id = port_events['dslam_id']
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        slot_number = port_events['slot_number']
        port_number = port_events['port_number']
        port_event_items = port_events['port_event_items']
        for item in port_event_items:
            dslam_port_event = DSLAMPortEvent(
                dslam = dslam_obj,
                slot_number = slot_number,
                port_number = port_number,
                type = item['event'],
                message = item.get('message',None)
            )
            dslam_port_event.save()


    @classmethod
    def update_dslam_status(cls, dslam_id, options):
        try:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
            dslam_obj.status = options.get('status')
            if dslam_obj.status == 'ready':
                dslam_obj.uptime = options.get('uptime')
                dslam_obj.hostname = options.get('hostname')
                duration = datetime.datetime.now()-dslam_obj.last_sync
                dslam_obj.last_sync_duration = duration.total_seconds()
            elif dslam_obj.status == 'updating':
                dslam_obj.last_sync = datetime.datetime.now()
            dslam_obj.save()
        except Exception as ex:
            print('++++++++++++++++++++++++++++++++++++++++')
            print(ex)
            print('++++++++++++++++++++++++++++++++++++++++')


    @classmethod
    def update_dslam_board(cls, dslam_id, result_boards):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        print('++++++++++++++++++++++++')
        print((result_boards.get('result')))
        print('++++++++++++++++++++++++')
        if type(result_boards.get('result')) == list:
            for board in result_boards.get('result'):
                card_number=board.get('card_number')
                try:
                    obj, created = DSLAMBoard.objects.update_or_create(dslam=dslam_obj, card_number=card_number,
                            defaults={'status': board.get('status'),
                                'card_type': board.get('card_type'),
                                'uptime': board.get('uptime'),
                                'fw_version': board.get('fw_version'),
                                'temperature': board.get('temperature'),
                                'serial_number': board.get('serial_number'),
                                'hw_version': board.get('hw_version'),
                                'mac_address': board.get('mac_address'),
                                'inband_mac_address': board.get('inband_mac_address'),
                                'outband_mac_address': board.get('outband_mac_address')
                                }
                            )
                except Exception as ex:
                    print(ex)


    @classmethod
    def change_port_admin_status(cls, dslam_id, port_indexes, admin_status):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        for port_item in port_indexes:
            dslamport_obj = DSLAMPort.objects.get(dslam=dslam_obj, port_index=port_item['port_index'])
            dslamport_obj.admin_status = admin_status.upper()
            dslamport_obj.save()


    @classmethod
    def change_port_line_profile(cls, dslam_id, port_indexes, line_profile):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        try:
            for port_item in port_indexes:
                dslamport_obj = DSLAMPort.objects.get(dslam=dslam_obj, port_index=port_item['port_index'])
                dslamport_obj.line_profile = line_profile
                dslamport_obj.save()
        except Exception as ex:
            print('++++++++++++++++')
            print(ex)
            print('++++++++++++++++')


    @classmethod
    def change_port_vlan(cls, dslam_id, port_indexes, vlan_id):
        try:
            print(port_indexes)
            for port_item in port_indexes:
                print(port_item)
                port_obj = DSLAMPort.objects.get(dslam__id=dslam_id, port_index=port_item['port_index'])
                port_vlan_obj = DSLAMPortVlan()
                port_vlan_obj.port = port_obj
                port_vlan_obj.vlan = Vlan.objects.get(vlan_id=vlan_id)
                port_vlan_obj.save()
        except Exception as ex:
            print('+++++++++++++++++')
            print(ex)
            print('+++++++++++++++++')


    @classmethod
    def partial_update_port_status(cls, dslam_id, command, port_indexes, values):
        for index, port in enumerate(port_indexes):
            port_obj = DSLAMPort.objects.get(dslam__id=dslam_id, port_index=port['port_index'])
            if command == 'selt':
                port_obj.selt_value = values[index].get('loopEstimateLength')
                port_obj.save()
            elif command == "show mac slot port":
                if bool(values['result']):
                    if 'mac' in values['result'][index]:
                        dslamport_mac_obj, created_port_mac_obj = DSLAMPortMac.objects.get_or_create(
                               port=port_obj,
                               mac_address=values['result'][index].get('mac')
                        )


    @classmethod
    def update_port_status(cls, dslam_id, port_status_list):
        new_port_list = []
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        #dslam_ports_queryset = DSLAMPort.objects.filter(dslam=dslam_obj)
        for port_status in port_status_list:
            port_obj = DSLAMPort.objects.filter(
                dslam=dslam_obj
            ).filter(port_index=port_status['PORT_INDEX'])
            if port_obj:# we need to update
                port_obj = port_obj[0]
                Transaction._update_port_status(dslam_id, port_obj, port_status)
            else: # we need to create
                slot_number, port_number = Transaction._create_port(dslam_id, port_status)
                new_port_list.append({
                    "dslam_id":dslam_id,
                    "slot_number": slot_number,
                    "port_number": port_number,
                    "port_event_items":[{'event':'new_port', 'message':'Find New Port'}]
                    })
        cls.update_dslam_status(dslam_id, {'status': 'ready'})


    @classmethod
    def _update_dslam_ports(cls, dslam_id, port_status_list):
        dslam_obj = DSLAM.objects.get(id=dslam_id)
        for port_status in port_status_list:
            port_obj = DSLAMPort.objects.filter(
                dslam=dslam_obj
            ).filter(port_index=port_status['PORT_INDEX'])
            if port_obj:# we need to update
                port_obj = port_obj[0]
            else:
                print(('port not found for update: %s'%str(port_status)))
                continue

            Transaction._update_port_status(dslam_id, port_obj, port_status)

    @classmethod
    def _create_port(cls, dslam_id, port_status):
        try:
            dslam = DSLAM.objects.get(id=dslam_id)
            port_obj = DSLAMPort(dslam=dslam)
            port_obj.slot_number = port_status.get('SLOT_NUMBER', None)
            port_obj.port_number = port_status.get('PORT_NUMBER', None)
            port_obj.port_name = port_status.get('PORT_NAME', None)
            port_obj.port_index = port_status.get('PORT_INDEX', None)
            port_obj.admin_status = port_status.get('PORT_ADMIN_STATUS', None)
            port_obj.oper_status = port_status.get('PORT_OPER_STATUS', None)
            port_obj.line_profile = port_status.get('LINE_PROFILE', None)
            port_obj.uptime = port_status.get('ADSL_UPTIME', None)
            port_obj.upstream_snr = port_status.get('ADSL_UPSTREAM_SNR', None)
            port_obj.downstream_snr = port_status.get('ADSL_DOWNSTREAM_SNR', None)
            port_obj.upstream_attenuation = port_status.get('ADSL_UPSTREAM_ATTEN', None)
            port_obj.downstream_attenuation = port_status.get('ADSL_DOWNSTREAM_ATTEN', None)
            port_obj.upstream_attainable_rate = port_status.get('ADSL_UPSTREAM_ATT_RATE', None)
            port_obj.downstream_attainable_rate = port_status.get('ADSL_DOWNSTREAM_ATT_RATE', None)
            port_obj.upstream_tx_rate = port_status.get('ADSL_CURR_UPSTREAM_RATE', None)
            port_obj.downstream_tx_rate = port_status.get('ADSL_CURR_DOWNSTREAM_RATE', None)
            port_obj.upstream_snr_flag = port_status.get('ADSL_UPSTREAM_SNR_FLAG', None)
            port_obj.downstream_snr_flag = port_status.get('ADSL_DOWNSTREAM_SNR_FLAG', None)
            port_obj.upstream_attenuation_flag = port_status.get('ADSL_UPSTREAM_ATTEN_FLAG', None)
            port_obj.downstream_attenuation_flag = port_status.get('ADSL_DOWNSTREAM_ATTEN_FLAG', None)

            port_obj.save()
        except Exception as ex:
            print(ex)
            print('---------------------------')
            print("error for dslam port object")
            print('dslam_id: ')
            print(dslam_id)
            print('print status: ')
            print(port_status)
            print('---------------------------')

        Transaction._port_status_snapshot(dslam_id, port_status)
        return (port_obj.slot_number, port_obj.port_number, )


    @classmethod
    def _update_port_status(cls, dslam_id, port_obj, port_status):
        try:
            port_obj.slot_number = port_status.get('SLOT_NUMBER', port_obj.slot_number)
            port_obj.port_number = port_status.get('PORT_NUMBER', port_obj.port_number)
            port_obj.port_name = port_status.get('PORT_NAME', port_obj.port_name)
            port_obj.port_index = port_status.get('PORT_INDEX', port_obj.port_index)
            port_obj.admin_status = port_status.get('PORT_ADMIN_STATUS', port_obj.admin_status)
            port_obj.oper_status = port_status.get('PORT_OPER_STATUS', port_obj.oper_status)
            port_obj.line_profile = port_status.get('LINE_PROFILE', port_obj.line_profile)
            port_obj.uptime = port_status.get('ADSL_UPTIME', port_obj.uptime)
            port_obj.upstream_snr = port_status.get('ADSL_UPSTREAM_SNR', port_obj.upstream_snr)
            port_obj.downstream_snr = port_status.get('ADSL_DOWNSTREAM_SNR', port_obj.downstream_snr)
            port_obj.upstream_attenuation = port_status.get('ADSL_UPSTREAM_ATTEN', port_obj.upstream_attenuation)
            port_obj.downstream_attenuation = port_status.get('ADSL_DOWNSTREAM_ATTEN', port_obj.downstream_attenuation)
            port_obj.upstream_attainable_rate = port_status.get('ADSL_UPSTREAM_ATT_RATE', port_obj.upstream_attainable_rate)
            port_obj.downstream_attainable_rate = port_status.get('ADSL_DOWNSTREAM_ATT_RATE', port_obj.downstream_attainable_rate)
            port_obj.upstream_tx_rate = port_status.get('ADSL_CURR_UPSTREAM_RATE', port_obj.upstream_tx_rate)
            port_obj.downstream_tx_rate = port_status.get('ADSL_CURR_DOWNSTREAM_RATE', port_obj.downstream_tx_rate)
            port_obj.upstream_snr_flag = port_status.get('ADSL_UPSTREAM_SNR_FLAG', port_obj.upstream_snr_flag)
            port_obj.downstream_snr_flag = port_status.get('ADSL_DOWNSTREAM_SNR_FLAG', port_obj.downstream_snr_flag)
            port_obj.upstream_attenuation_flag = port_status.get('ADSL_UPSTREAM_ATTEN_FLAG', port_obj.upstream_attenuation_flag)
            port_obj.downstream_attenuation_flag = port_status.get('ADSL_DOWNSTREAM_ATTEN_FLAG', port_obj.upstream_attenuation_flag)
            port_obj.save()
        except Exception as ex:
            print('---------------------------')
            print(ex)
            print("error for dslam port object")
            print('dslam_id: ')
            print(dslam_id)
            print('portstatus: ')
            print(port_status)
            print('obj: ')
            print(port_obj)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((exc_type, fname, exc_tb.tb_lineno))
            print((traceback.format_exc()))
            print('---------------------------')

        Transaction._port_status_snapshot(dslam_id,port_status)


    @classmethod
    def _port_status_snapshot(cls, dslam_id, port_status):
        try:
            snp = DSLAMPortSnapshot()
            snp.dslam_id = dslam_id
            snp.slot_number = port_status.get('SLOT_NUMBER')
            snp.port_number = port_status.get('PORT_NUMBER')
            snp.port_index = port_status.get('PORT_INDEX')
            snp.port_name = port_status.get('PORT_NAME')
            snp.admin_status = port_status.get('PORT_ADMIN_STATUS', None)
            snp.oper_status = port_status.get('PORT_OPER_STATUS', None)
            snp.line_profile = port_status.get('LINE_PROFILE', None)
            snp.uptime = port_status.get('ADSL_UPTIME', None)
            snp.upstream_snr = port_status.get('ADSL_UPSTREAM_SNR', None)
            snp.downstream_snr = port_status.get('ADSL_DOWNSTREAM_SNR', None)
            snp.upstream_attenuation = port_status.get('ADSL_UPSTREAM_ATTEN', None)
            snp.downstream_attenuation = port_status.get('ADSL_DOWNSTREAM_ATTEN', None)
            snp.upstream_attainable_rate = port_status.get('ADSL_UPSTREAM_ATT_RATE', None)
            snp.downstream_attainable_rate = port_status.get('ADSL_DOWNSTREAM_ATT_RATE', None)
            snp.upstream_tx_rate = port_status.get('ADSL_CURR_UPSTREAM_RATE', None)
            snp.downstream_tx_rate = port_status.get('ADSL_CURR_DOWNSTREAM_RATE', None)
            snp.upstream_snr_flag = port_status.get('ADSL_UPSTREAM_SNR_FLAG', None)
            snp.downstream_snr_flag = port_status.get('ADSL_DOWNSTREAM_SNR_FLAG', None)
            snp.upstream_attenuation_flag = port_status.get('ADSL_UPSTREAM_ATTEN_FLAG', None)
            snp.downstream_attenuation_flag = port_status.get('ADSL_DOWNSTREAM_ATTEN_FLAG', None)
            snp.save()
        except Exception as ex:
            print('---------------------------')
            print(ex)
            print("error for dslam port object")
            print('dslam_id: ')
            print(dslam_id)
            print('portstatus: ')
            print(port_status)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((exc_type, fname, exc_tb.tb_lineno))
            print((traceback.format_exc()))
            print('---------------------------')

    @classmethod
    def update_port_vpi_vci(cls, dslam_id, ports_info):
        try:
            dslam = DSLAM.objects.get(id=dslam_id)
            for port_info in ports_info:
                port_obj = DSLAMPort.objects.get(dslam=dslam, port_index=port_info.get('port_index'))
                port_obj.vpi = port_info.get('vpi')
                port_obj.vci = port_info.get('vci')
                port_obj.save()
        except Exception as ex:
            print('???????????????????????')
            print(ex)
            print((port_info.get('port_index')))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((exc_type, fname, exc_tb.tb_lineno))
            print((traceback.format_exc()))
            print('???????????????????????')

    @classmethod
    def update_dslamport_command_result(cls, dslam_id, port_indexes, command, result_values, username=None):
        cmd = Command.objects.get(text=command)
        dslam = DSLAM.objects.get(id=dslam_id)
        port_command = PortCommand(dslam=dslam,
                card_ports=port_indexes,
                command=cmd,
                value=result_values,
                username=username
                )
        port_command.save()

    @classmethod
    def update_dslam_command_result(cls, dslam_id, command, result_values, username=None):
        cmd = Command.objects.get(text=command)
        dslam = DSLAM.objects.get(id=dslam_id)
        dslam_command = DSLAMCommand(dslam=dslam,
                command=cmd,
                value=result_values,
                username=username
                )
        dslam_command.save()

    @classmethod
    def add_dslam_bulk_command_result(cls, title, success_filepath, error_filepath, result_filepath, commands):
        dslam_bulk_command_result = DSLAMBulkCommandResult()
        dslam_bulk_command_result.title = title
        dslam_bulk_command_result.commands = commands
        open(success_filepath, 'a').close()
        f = open(success_filepath)
        dslam_bulk_command_result.success_file.save(basename(success_filepath), File(f))
        open(error_filepath, 'a').close()
        f = open(error_filepath)
        dslam_bulk_command_result.error_file.save(basename(error_filepath), File(f))
        f = open(result_filepath, 'a').close()
        f = open(result_filepath)
        dslam_bulk_command_result.result_file.save(basename(result_filepath), File(f))
        dslam_bulk_command_result.save()

    @classmethod
    def update_profile_adsl(cls, profiles):
        for profile in profiles:
            try:
                obj, created = LineProfile.objects.update_or_create(name=profile.get('name'), \
                        defaults={
                            'channel_mode': profile.get('channel_mode'),
                            'template_type': profile.get('template_type'),
                            'max_us_transmit_rate': profile.get('max_us_transmit_rate'),
                            'max_ds_transmit_rate': profile.get('max_ds_transmit_rate'),
                            'min_us_transmit_rate': profile.get('min_us_transmit_rate'),
                            'min_ds_transmit_rate': profile.get('min_ds_transmit_rate'),
                            'us_snr_margin': profile.get('us_snr_margin'),
                            'ds_snr_margin': profile.get('ds_snr_margin'),
                            'max_us_interleaved': profile.get('max_us_interleaved'),
                            'max_ds_interleaved': profile.get('max_ds_interleaved'),
                            })
                if 'extra_settings' in list(profile.keys()):
                    for key, value in list(profile.get('extra_settings').items()):
                        LineProfileExtraSettings.objects.update_or_create(line_profile=obj, attr_name=key, defaults={'attr_value': value})
            except Exception as ex:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print(('profiles: ', profiles))
                print(ex)
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    @classmethod
    def add_line_profile(cls, params):
        try:
            obj, created = LineProfile.objects.update_or_create(name=params.get('profile'),\
                    defaults={
                        'channel_mode': params.get('channel_mode'),
                        'template_type': params.get('template_type'),
                        'max_us_transmit_rate': params.get('max_us_transmit_rate'),
                        'max_ds_transmit_rate': params.get('max_ds_transmit_rate'),
                        'min_us_transmit_rate': params.get('min_us_transmit_rate'),
                        'min_ds_transmit_rate': params.get('min_ds_transmit_rate'),
                        'us_snr_margin': params.get('us_snr_margin'),
                        'ds_snr_margin': params.get('ds_snr_margin'),
                        'max_us_interleaved': params.get('max_us_interleaved'),
                        'max_ds_interleaved': params.get('max_ds_interleaved'),
                        'extra_settings': params.get('extra_settings')
                        })
            for key, value in list(params.get('extra_settings').items()):
                LineProfileExtraSettings.objects.update_or_create(line_profile=obj, attr_name=key, defaults={'attr_value': value})

        except Exception as ex:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(('params: ', params))
            print(ex)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

