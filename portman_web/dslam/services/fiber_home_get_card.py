from dslam.models import DSLAM
from dslam import utility
import re
import sys, os


class FiberHomeGetCardStatusService:
    def __init__(self, data):
        self.data = data

    @property
    def get_data(self):
        return self.data

    def get_status_cards(self):

        command = 'Show Shelf'
        fqdn = self.data.get('fqdn')
        params = self.data.get('params', None)
        dslam_id = self.data.get('dslam_id', None)

        if dslam_id is None:
            dslam_id = DSLAM.objects.get(fqdn=self.data.get('fqdn')).id
        else:
            dslam_id = dslam_id

        dslamObj = DSLAM.objects.get(id=dslam_id)
        dslam_type = dslamObj.dslam_type_id

        try:
            result = utility.dslam_port_run_command(dslamObj.pk, command, params)
            if dslam_type == 3:  ############################## fiberhomeAN3300 ##############################
                result = [val for val in result['result'] if re.search(r'^\s+\d+\s+', val)]
                cards_info = []
                for item in result:
                    print(item)
                    card_info = {}
                    card_info["Card"] = item.split()[0]
                    if 'up' in item:
                        card_info["Status"] = 'ON'
                    else:
                        card_info["Status"] = 'OFF'

                    cards_info.append(card_info)
                cards_info.append({'DslamType': "fiberhomeAN3300"})
                return cards_info

            elif dslam_type == 4:  ############################## fiberhomeAN2200 ##############################
                result = [val for val in result['result'] if re.search(r'^\s+\d+\s+', val)]
                cards_info = []
                for item in result:
                    card_info = {}
                    card_info["Card"] = item.split()[1]
                    if 'LINK_LOS' not in item:
                        card_info["Status"] = 'ON'
                    else:
                        card_info["Status"] = 'OFF'

                    cards_info.append(card_info)
                cards_info.append({'DslamType': "fiberhomeAN2200"})
                return cards_info

            elif dslam_type == 5:  ############################## fiberhomeAN5006 ##############################
                result = [val for val in result['result'] if re.search(r'\s{10,}', val)]
                cards_info = []
                for item in result:
                    card_info = {}
                    card_info["Card"] = item.split()[0]
                    if 'ADSL' in item or 'VDSL' in item:
                        card_info["Status"] = 'ON'
                    else:
                        card_info["Status"] = 'OFF'

                    cards_info.append(card_info)
                cards_info.append({'DslamType': "fiberhomeAN5006"})
                return cards_info
            elif dslam_type == 2:  ############################## Huawei ##############################
                result = [val for val in result['result'] if re.search(r'\s+\d', val)]
                cards_info = []
                for item in result:
                    card_info = {}
                    card_info["Card"] = item.split()[0]
                    if 'Normal' in item:
                        card_info["Status"] = 'ON'
                    else:
                        card_info["Status"] = 'OFF'

                    cards_info.append(card_info)
                cards_info.append({'DslamType': "huawei"})
                return cards_info

            elif dslam_type == 1:  ############################## zyxel ##############################
                result = [item for item in result['result'] if re.search(r'^\s*\d+\s+', item)]
                cards_info = []

                for item in result:
                    card_info = {}
                    card_info['Card'] = item.split()[0]
                    if 'active' in item:
                        card_info["Status"] = 'ON'
                    else:
                        card_info["Status"] = 'OFF'

                    cards_info.append(card_info)
                cards_info.append({'DslamType': "huawei"})
                return cards_info
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return {'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno)}
