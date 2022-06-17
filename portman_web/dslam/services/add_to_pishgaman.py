import sys, os
from classes.portman_logging import PortmanLogging
from datetime import datetime
from dslam import utility
from dslam.models import DSLAM
from dslam.mail import Mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


class AddToPishgamanService():
    def __init__(self, data, device_ip):
        self.data = data
        self.device_ip = device_ip

    def add_to_pishgaman(self):
        port_data = self.data.get('port')
        fqdn = port_data.get('fqdn', None)
        card = port_data.get('card_number', None)
        port = port_data.get('port_number', None)
        subs_data = self.data.get('subscriber')
        username = subs_data.get('username')
        dslam_obj = DSLAM.objects.get(fqdn=str(fqdn).lower())
        dslam_type = dslam_obj.dslam_type_id
        log_port_data = "/".join([val for val in port_data.values()])
        log_username = username
        log_date = datetime.now()
        log_reseller_name = 'pte'

        try:
            if '.z6' in fqdn:
                fqdn = fqdn.replace('.z6', '.Z6')

            try:
                dslam_obj = DSLAM.objects.get(fqdn=fqdn)
            except ObjectDoesNotExist as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                              log_date,
                                                              self.device_ip, 'Register Port', False,
                                                              str(ex) + '/' + str(exc_tb.tb_lineno),
                                                              log_reseller_name)
                PortmanLogging('', log_params)

                try:
                    if '.Z6' in fqdn:
                        fqdn = fqdn.replace('.Z6', '.z6')
                        dslam_obj = DSLAM.objects.get(fqdn=fqdn)

                except ObjectDoesNotExist as ex:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                                  log_date,
                                                                  self.device_ip, 'Register Port', False,
                                                                  str(ex) + '/' + str(exc_tb.tb_lineno),
                                                                  log_reseller_name)
                    PortmanLogging('', log_params)
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    mail_info = Mail()
                    mail_info.from_addr = 'oss-problems@pishgaman.net'
                    mail_info.to_addr = 'oss-problems@pishgaman.net'
                    mail_info.msg_body = 'Error in RegisterPortAPIView in Line {0}.Error Is: "{1}". Request is From {2} .fqdn = {3}, Cart = {4}, Port = {5},Ip: {6}'.format(
                        str(exc_tb.tb_lineno), str(ex), 'pte', port_data.get('fqdn'),
                        port_data.get('card_number'), port_data.get('port_number'), self.device_ip)
                    mail_info.msg_subject = 'Error in RegisterPortAPIView'
                    Mail.Send_Mail(mail_info)
                    return {'result': 'Dslam Not Found. Please check FQDN again.', 'status': status.HTTP_404_NOT_FOUND}

        except ObjectDoesNotExist as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                          log_date,
                                                          self.device_ip, 'Register Port', False,
                                                          str(ex) + '/' + str(exc_tb.tb_lineno),
                                                          log_reseller_name)
            PortmanLogging('', log_params)
            return {'result': str(ex), 'status': status.HTTP_404_NOT_FOUND}
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                          log_date,
                                                          self.device_ip, 'Register Port', False,
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
                                                              self.device_ip, 'Register Port', False,
                                                              str(ex) + '/' + str(exc_tb.tb_lineno),
                                                              log_reseller_name)
                PortmanLogging('', log_params)
                mail_info = Mail()
                mail_info.from_addr = 'oss-problems@pishgaman.net'
                mail_info.to_addr = 'oss-problems@pishgaman.net'
                mail_info.msg_body = 'Error in RegisterPortAPIView in Line {0}.Error Is: "{1}". Request is From {2} .fqdn = {3}, Cart = {4}, Port = {5},Ip: {6}'.format(
                    str(exc_tb.tb_lineno), str(ex), 'pte', port_data.get('fqdn'), port_data.get('card_number'),
                    port_data.get('port_number'), self.device_ip)
                mail_info.msg_subject = 'Error in RegisterPortAPIView'
                Mail.Send_Mail(mail_info)
                return {'Result': '', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
        try:
            port_indexes = [{'slot_number': port_data.get('card_number'), 'port_number': port_data.get('port_number')}]
            pishParams = {
                "type": "dslamport",
                "is_queue": False,
                "vlan_id": dslam_obj.pishgaman_vlan,
                "vlan_name": 'pte',
                "dslam_id": dslam_obj.id,
                "port_indexes": port_indexes,
                "username": subs_data.get('username'),
                "vpi": dslam_obj.pishgaman_vpi,
                "vci": dslam_obj.pishgaman_vci,
            }
            result = utility.dslam_port_run_command(dslam_obj.id, 'add to vlan', pishParams)
            log_status = True if isinstance(result, dict) else False
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', result,
                                                          log_date,
                                                          self.device_ip, 'Register Port', log_status, '', log_reseller_name)
            PortmanLogging(result, log_params)
            return {'result': result['result'], 'status': status.HTTP_200_OK}
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_params = PortmanLogging.prepare_variables(self, log_port_data, log_username, 'add to vlan', '',
                                                          log_date,
                                                          self.device_ip, 'Register Port', False,
                                                          str(ex) + '/' + str(exc_tb.tb_lineno),
                                                          log_reseller_name)
            PortmanLogging('', log_params)
            return {'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}