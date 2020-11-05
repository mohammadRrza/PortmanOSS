import telnetlib
import time
from .base_command import BaseCommand
class CreateProfile(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'channel_mode', 'template_type', 'ds_snr_margin', 'us_snr_margin', 'max_ds_interleaved', 'max_us_interleaved', \
            'min_ds_transmit_rate', 'min_us_transmit_rate', 'max_ds_transmit_rate', 'max_us_transmit_rate', 'fiberhomeAN3300_q', 'profile',\
            'extra_setting', 'params')
    def __init__(self, tn, params, fiberhomeAN3300_q):
        self.tn = tn
        self.params = params
        self.dslam_id = params.get('dslam_id')
        self.channel_mode = params.get('channel_mode')
        self.extra_setting = params.get('extra_setting')
        self.template_type = params.get('template_type', 'AD32+')
        self.ds_snr_margin = params.get('ds_snr_margin')
        self.us_snr_margin = params.get('us_snr_margin')
        self.max_ds_interleaved = params.get('max_ds_interleaved')
        self.max_us_interleaved = params.get('max_us_interleaved')
        self.min_ds_transmit_rate = params.get('min_ds_transmit_rate')
        self.min_us_transmit_rate = params.get('min_us_transmit_rate')
        self.max_ds_transmit_rate = params.get('max_ds_transmit_rate')
        self.max_us_transmit_rate = params.get('max_us_transmit_rate')
        self.profile = params.get('profile')
        self.fiberhomeAN3300_q = fiberhomeAN3300_q

    def run_command(self, protocol):
        self.tn.write("cd profile\r\n".encode('utf-8'))
        time.sleep(1)

        self.tn.write("add xaplus profile {0}\r\n".format(self.profile).encode('utf-8'))
        time.sleep(1)
        self.tn.write("pvc 0 vpi 0 vci 35\r\n".encode('utf-8'))
        time.sleep(1)

        self.tn.write("adapt_mode {0}\r\n".format(self.extra_setting.get('adapt_mode')).encode('utf-8'))
        time.sleep(1)
        self.tn.write("channel_mode {0}\r\n".format(self.get('channel_mode')).encode('utf-8'))
        time.sleep(1)


        self.tn.write("downstream max linerate {0}\r\n".format(self.max_ds_transmit_rate).encode('utf-8'))
        time.sleep(1)
        self.tn.write("upstream max linerate {0}\r\n".format(self.max_us_transmit_rate).encode('utf-8'))
        time.sleep(1)
        self.tn.write("downstream min linerate {0}\r\n".format(self.min_ds_transmit_rate).encode('utf-8'))
        time.sleep(1)
        self.tn.write("upstream min linerate {0}\r\n".format(self.min_us_transmit_rate).encode('utf-8'))
        time.sleep(1)

        if channel_mode != 'fast':
            self.tn.write("downstream max interleavedelay {0}\r\n".format(self.max_ds_interleaved).encode('utf-8'))
            time.sleep(1)
            self.tn.write("upstream max interleavedelay {0}\r\n".format(self.max_us_interleaved).encode('utf-8'))
            time.sleep(1)

        self.tn.write("downstream targetnoise margin {0}\r\n".format(self.ds_snr_margin).encode('utf-8'))
        time.sleep(1)
        self.tn.write("upstream targetnoise margin {0}\r\n".format(self.us_snr_margin).encode('utf-8'))
        time.sleep(1)

        self.tn.write("downstream max margin {0}\r\n".format(self.extra_setting.get('max_ds_snr_margin')).encode('utf-8'))
        time.sleep(1)
        self.tn.write("upstream max margin {0}\r\n".format(self.extra_setting.get('max_us_snr_margin')).encode('utf-8'))
        time.sleep(1)

        self.tn.write("downstream upshiftnoise margin {0}\r\n".format(self.extra_setting.get('usra_ds_mgn')).encode('utf-8'))
        time.sleep(1)
        self.tn.write("downstream dnshiftnoise margin {0}\r\n".format(self.extra_setting.get('dsra_ds_mgn')).encode('utf-8'))
        time.sleep(1)


        self.tn.write("exit\r\n".encode('utf-8'))
        result = {"result": self.tn.read_until('exit')}
        print('***********************************')
        print(result)
        print('***********************************')
        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN3300_q.put(("update_dslam_command_result",
                self.dslam_id,
                "profile adsl set",
                result))
            if 'add profile success' in result.lower():
                self.fiberhomeAN3300_q.put(("add_line_profile",
                    self.params))

