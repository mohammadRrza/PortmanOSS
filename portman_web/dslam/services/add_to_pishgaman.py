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

        # try:
        #     if '.z6' in fqdn:
        #         fqdn = fqdn.replace('.z6', '.Z6')