import sys, os
from classes.portman_logging import PortmanLogging
from datetime import datetime
from dslam.models import DSLAM
from dslam import utility
from .device_ip import get_device_ip
from dslam.models import DSLAM, TelecomCenter, TelecomCenterMDF, MDFDSLAM, Reseller, CustomerPort, Vlan, ResellerPort
from dslam.mail import Mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
import random


class AddToVlanService:
    def __init__(self, request):
        self.request = request

    def add_to_vlan(self):
        data = self.request.data
        ip = get_device_ip(self.request)
        port_data = data.get('port', None)
        command = 'Show Shelf'
        fqdn = port_data.get('fqdn', None)
        reseller_data = data.get('reseller')
        customer_data = data.get('subscriber')
        dslam_obj = DSLAM.objects.get(fqdn=str(fqdn).lower())
        mdf_status = data.get('status')
        identifier_key = data.get('identifier_key')
        if not identifier_key:
            identifier_key = str(random.randint(10000000, 9999999999999999))
        dslam_type = dslam_obj.dslam_type_id
        if not mdf_status:
            mdf_status = 'BUSY'

        log_port_data = "/".join([val for val in port_data.values()])
        log_username = customer_data.get('username')
        log_date = datetime.now()
        log_reseller_name = reseller_data.get('name')
        try:
            if '.z6' in fqdn:
                fqdn = fqdn.replace('.z6', '.Z6')

            # dslam_obj = DSLAM.objects.get(name=port_data.get('dslam_name'), telecom_center__name=port_data.get('telecom_center_name'))
            try:
                dslam_obj = DSLAM.objects.get(fqdn=fqdn)
                # return JsonResponse({'Result': serialize('json',[dslam_obj])}, status=status.HTTP_200_OK)
                telecom_id = dslam_obj.telecom_center_id
                city_id = TelecomCenter.objects.get(id=telecom_id).city_id
            except ObjectDoesNotExist as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                              log_date,
                                                              ip, 'Register Port', False,
                                                              str(ex) + '/' + str(exc_tb.tb_lineno),
                                                              log_reseller_name)
                PortmanLogging('', log_params)
                try:
                    if '.Z6' in fqdn:
                        fqdn = fqdn.replace('.Z6', '.z6')
                        dslam_obj = DSLAM.objects.get(fqdn=fqdn)
                        # return JsonResponse({'Result': dslam_obj.fqdn}, status=status.HTTP_200_OK)
                        telecom_id = dslam_obj.telecom_center_id
                        city_id = TelecomCenter.objects.get(id=telecom_id).city_id

                except ObjectDoesNotExist as ex:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                                  log_date,
                                                                  ip, 'Register Port', False,
                                                                  str(ex) + '/' + str(exc_tb.tb_lineno),
                                                                  log_reseller_name)
                    PortmanLogging('', log_params)
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    mail_info = Mail()
                    mail_info.from_addr = 'oss-problems@pishgaman.net'
                    mail_info.to_addr = 'oss-problems@pishgaman.net'
                    mail_info.msg_body = 'Error in RegisterPortAPIView in Line {0}.Error Is: "{1}". Request is From {2} .fqdn = {3}, Cart = {4}, Port = {5},Ip: {6}'.format(
                        str(exc_tb.tb_lineno), str(ex), reseller_data, port_data.get('fqdn'),
                        port_data.get('card_number'), port_data.get('port_number'), ip)
                    mail_info.msg_subject = 'Error in RegisterPortAPIView'
                    Mail.Send_Mail(mail_info)
                    return {'result': 'Dslam Not Found. Please check FQDN again.', 'status': status.HTTP_404_NOT_FOUND}

            telecom_mdf_obj = TelecomCenterMDF.objects.filter(telecom_center_id=dslam_obj.telecom_center.id)
            print((dslam_obj.telecom_center.id))
            if telecom_mdf_obj:
                telecom_mdf_obj = telecom_mdf_obj.first()
            print((dslam_obj.telecom_center))
            mdf_dslam_obj, mdf_dslam_updated = MDFDSLAM.objects.update_or_create(
                telecom_center_id=dslam_obj.telecom_center.id,
                telecom_center_mdf_id=telecom_mdf_obj.id,
                #### Check this whole line
                row_number=0, floor_number=0, connection_number=0,  ##### Check this whole line
                dslam_id=dslam_obj.id, slot_number=port_data.get('card_number'),
                port_number=port_data.get('port_number'),
                defaults={'status': mdf_status, 'identifier_key': identifier_key})
            # if mdf_dslam.status != 'FREE':
            #    return JsonResponse(
            #            {'result': 'port status is {0}'.format(mdf_dslam.status), 'id': -1}
            #            )
            # else:
            #    mdf_dslam.status = 'RESELLER'
            #    mdf_dslam.save()
            # identifier_key = mdf_dslam.identifier_key
        except ObjectDoesNotExist as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                          log_date,
                                                          ip, 'Register Port', False,
                                                          str(ex) + '/' + str(exc_tb.tb_lineno),
                                                          log_reseller_name)
            PortmanLogging('', log_params)
            return {'result': str(ex), 'id': -1, 'status': status.HTTP_404_NOT_FOUND}
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                          log_date,
                                                          ip, 'Register Port', False,
                                                          str(ex) + '/' + str(exc_tb.tb_lineno),
                                                          log_reseller_name)
            PortmanLogging('', log_params)
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            try:
                return {'result': 'Error is {0}--{1}'.format(ex, exc_tb.tb_lineno), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
            except ObjectDoesNotExist as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                              log_date,
                                                              ip, 'Register Port', False,
                                                              str(ex) + '/' + str(exc_tb.tb_lineno),
                                                              log_reseller_name)
                PortmanLogging('', log_params)
                mail_info = Mail()
                mail_info.from_addr = 'oss-problems@pishgaman.net'
                mail_info.to_addr = 'oss-problems@pishgaman.net'
                mail_info.msg_body = 'Error in RegisterPortAPIView in Line {0}.Error Is: "{1}". Request is From {2} .fqdn = {3}, Cart = {4}, Port = {5},Ip: {6}'.format(
                    str(exc_tb.tb_lineno), str(ex), reseller_data, port_data.get('fqdn'), port_data.get('card_number'),
                    port_data.get('port_number'), ip)
                mail_info.msg_subject = 'Error in RegisterPortAPIView'
                Mail.Send_Mail(mail_info)
                return {'result': '', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}

        try:
            reseller_obj, reseller_created = Reseller.objects.get_or_create(name=reseller_data.get('name'))

            customer_obj, customer_updated = CustomerPort.objects.update_or_create(
                username=customer_data.get('username'),
                defaults={'identifier_key': identifier_key, 'telecom_center_id': mdf_dslam_obj.telecom_center_id}
            )

            rp = ResellerPort()
            rp.identifier_key = identifier_key
            rp.status = 'ENABLE'
            rp.dslam_id = dslam_obj.id
            rp.dslam_slot = port_data.get('card_number')
            rp.dslam_port = port_data.get('port_number')
            rp.reseller = reseller_obj
            rp.telecom_center_id = mdf_dslam_obj.telecom_center_id
            rp.save()

            vlan_objs = Vlan.objects.filter(reseller=reseller_obj)
            print()
            'vlan_objs ->', vlan_objs
            # return JsonResponse({'vlan':  vlan_objs[0].vlan_id, 'vpi' : reseller_obj.vpi,'vci' : reseller_obj.vci})
            port_indexes = [{'slot_number': port_data.get('card_number'), 'port_number': port_data.get('port_number')}]
            pishParams = {
                "type": "dslamport",
                "is_queue": False,
                "vlan_id": 3900,
                "vlan_name": 'pte',
                "dslam_id": dslam_obj.id,
                "port_indexes": port_indexes,
                "username": customer_data.get('username'),
                "vpi": 0,
                "vci": 35,
            }
            vlan_name = vlan_objs[0].vlan_name
            if dslam_type == 3 or dslam_type == 4 or dslam_type == 5:
                vlan_name = str(reseller_obj).split('-')[1]
                if vlan_name == 'didehban':
                    vlan_name = 'dideban'
                if vlan_name == 'baharsamaneh':
                    vlan_name = 'baharsam'
                if vlan_name == 'badrrayan':
                    vlan_name = 'badrray'
            params = {
                "type": "dslamport",
                "is_queue": False,
                "vlan_id": vlan_objs[0].vlan_id,
                "vlan_name": vlan_name,
                "dslam_id": dslam_obj.id,
                "port_indexes": port_indexes,
                "username": customer_data.get('username'),
                "vpi": reseller_obj.vpi,
                "vci": reseller_obj.vci,
            }

            # res = utility.dslam_port_run_command(dslam_obj.id, 'delete from vlan', pishParams)
            result = utility.dslam_port_run_command(dslam_obj.id, 'add to vlan', params)
            # PVC = utility.dslam_port_run_command(dslam_obj.id, 'port pvc show', params)

            # result2 = utility.dslam_port_run_command(dslam_obj.id, 'add to vlan', params)
            log_status = True if isinstance(result, dict) else False
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', result,
                                                          log_date,
                                                          ip, 'Register Port', log_status, '', log_reseller_name)
            PortmanLogging(result, log_params)
            return {'result': result, 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                          log_date,
                                                          ip, 'Register Port', False,
                                                          str(ex) + '/' + str(exc_tb.tb_lineno),
                                                          log_reseller_name)
            PortmanLogging('', log_params)
            return {'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}

