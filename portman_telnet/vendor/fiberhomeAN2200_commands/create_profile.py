import telnetlib
import time
from .base_command import BaseCommand
class CreateProfile(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'latency', 'template_type', 'ds_snr_margin', 'us_snr_margin', 'max_ds_interleaved', 'max_us_interleaved', \
            'min_ds_transmit_rate', 'min_us_transmit_rate', 'max_ds_transmit_rate', 'max_us_transmit_rate', 'fiberhomeAN2200_q', 'profile')
    def __init__(self, tn, params, fiberhomeAN2200_q):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.latency = params.get('channel_mode')
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
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        self.tn.write("createprf\r\n".encode('utf-8'))

        # set template type (else => AD32+)
        if self.template_type and self.template_type != 'AD32+':
            self.tn.write("2\r\n".encode('utf-8'))
        else:
            self.tn.write("5\r\n".encode('utf-8'))

        # set multimode
        self.tn.write("4\r\n".encode('utf-8'))
        time.sleep(1)


        # set latency Fast
        if not self.max_ds_interleaved and not self.max_us_interleaved:
            self.tn.write("1\r\n".encode('utf-8'))
            # set SNR margin up/down default
            self.tn.write("{0}\r\n".format(self.ds_snr_margin).encode('utf-8'))
            self.tn.write("{0}\r\n".format(self.us_snr_margin).encode('utf-8'))
        else:
            # set Interleav SNR marginefault
            self.tn.write("0\r\n".encode('utf-8'))
            self.tn.write("{0}\r\n".format(self.max_ds_interleaved).encode('utf-8'))
            self.tn.write("{0}\r\n".format(self.max_us_interleaved).encode('utf-8'))
            self.tn.write("{0}\r\n".format(self.ds_snr_margin).encode('utf-8'))
            self.tn.write("{0}\r\n".format(self.us_snr_margin).encode('utf-8'))

        # set Down stream min/max
        self.tn.write("{0}/{1}\r\n".format(self.min_ds_transmit_rate, self.max_ds_transmit_rate).encode('utf-8'))
        self.tn.write("{0}/{1}\r\n".format(self.min_us_transmit_rate, self.max_us_transmit_rate).encode('utf-8'))

        self.tn.write("{0}\r\n".format(self.profile).encode('utf-8'))

        self.tn.write("end\r\n".encode('utf-8'))
        result = {"result": self.tn.read_until('end')}
        print('***********************************')
        print(result)
        print('***********************************')
        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put(("update_dslam_command_result",
                self.dslam_id,
                "profile adsl set",
                result))

