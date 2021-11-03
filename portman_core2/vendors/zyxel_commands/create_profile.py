import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re

class CreateProfile(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__params = params
        self.device_ip = params.get('device_ip')

    @property
    def HOST(self):
        return self.__HOST

    @HOST.setter
    def HOST(self, value):
        self.__HOST = value

    @property
    def telnet_username(self):
        return self.__telnet_username

    @telnet_username.setter
    def telnet_username(self, value):
        self.__telnet_username = value

    @property
    def telnet_password(self):
        return self.__telnet_password

    @telnet_password.setter
    def telnet_password(self, value):
        self.__telnet_password = value

    retry = 1
    def run_command(self):
        # Initial Parameters
        profile_name = self.__params.get('name')
        template_type = self.__params.get('template_type')
        channel_mode = self.__params.get('channel_mode')
        max_us_transmit_rate = self.__params.get('max_us_transmit_rate')
        max_ds_transmit_rate = self.__params.get('max_ds_transmit_rate')
        min_us_transmit_rate = self.__params.get('min_us_transmit_rate')
        min_ds_transmit_rate = self.__params.get('min_ds_transmit_rate')
        us_snr_margin = self.__params.get('us_snr_margin')
        ds_snr_margin = self.__params.get('ds_snr_margin')
        max_us_interleaved = self.__params.get('max_us_interleaved')
        max_ds_interleaved = self.__params.get('max_ds_interleaved')
        extra_settings = self.__params.get('extra_settings')
        if extra_settings:
            usra = extra_settings.get('usra')
            dsra = extra_settings.get('dsra')
            min_us_snr_margin = extra_settings.get('min_us_snr_margin')
            max_ds_snr_margin = extra_settings.get('max_ds_snr_margin')
            min_ds_snr_margin = extra_settings.get('min_ds_snr_margin')
            max_us_snr_margin = extra_settings.get('max_us_snr_margin')
            usra_ds_mgn = extra_settings.get('usra_ds_mgn')
            dsra_us_mgn = extra_settings.get('dsra_us_mgn')
            dsra_ds_mgn = extra_settings.get('dsra_ds_mgn')
            usra_us_mgn = extra_settings.get('usra_us_mgn')
        # End Initial Parameters

        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.read_until('Password:')
            command_template = "profile adsl set {profile_name} {max_us_transmit_rate} {max_ds_transmit_rate} \
            {channel_mode} minrate {min_us_transmit_rate} {min_ds_transmit_rate} \
            usmgn {max_us_snr_margin} {min_us_snr_margin} {us_snr_margin} \
            dsmgn {max_ds_snr_margin} {min_ds_snr_margin} {ds_snr_margin} \
            usra {usra} {usra_us_mgn} {usra_ds_mgn} \
            dsra {dsra} {dsra_us_mgn} {dsra_s_mgn}\r\n\r\n"

            if channel_mode == 'fast':
                command = command_template.format(
                        profile_name = profile_name,
                        max_us_transmit_rate = max_us_transmit_rate,
                        max_ds_transmit_rate = max_ds_transmit_rate,
                        channel_mode = channel_mode,
                        min_us_transmit_rate = min_us_transmit_rate,
                        min_ds_transmit_rate = min_ds_transmit_rate,
                        max_us_snr_margin = max_us_snr_margin,
                        min_us_snr_margin = min_us_snr_margin,
                        us_snr_margin = us_snr_margin,
                        max_ds_snr_margin = max_ds_snr_margin,
                        min_ds_snr_margin = min_ds_snr_margin,
                        ds_snr_margin = ds_snr_margin,
                        usra = usra,
                        usra_us_mgn = usra_us_mgn,
                        usra_ds_mgn = usra_ds_mgn
                        )
            else:
                command = command_template.format(
                        profile_name = profile_name,
                        max_us_transmit_rate = max_us_transmit_rate,
                        max_ds_transmit_rate = max_ds_transmit_rate,
                        channel_mode = 'delay {max_us_interleaved} {max_ds_interleaved}',
                        min_us_transmit_rate = min_us_transmit_rate,
                        min_ds_transmit_rate = min_ds_transmit_rate,
                        max_us_snr_margin = max_us_snr_margin,
                        min_us_snr_margin = min_us_snr_margin,
                        us_snr_margin = us_snr_margin,
                        max_ds_snr_margin = max_ds_snr_margin,
                        min_ds_snr_margin = min_ds_snr_margin,
                        ds_snr_margin = ds_snr_margin,
                        usra = usra,
                        usra_us_mgn = usra_us_mgn,
                        usra_ds_mgn = usra_ds_mgn
                        ).format(
                                max_us_interleaved = max_us_interleaved,
                                max_ds_interleaved = max_ds_interleaved
                                )

            tn.write(command.encode('utf-8'))
            time.sleep(1)
            tn.write("end\r\n")
            result = tn.read_until('end')
            tn.write("exit\r\n")
            tn.write("y\r\n")
            tn.close()
            print('*******************************************')
            print(("{0} profile created".format(profile_name)))
            print('*******************************************')
            return {"result": "{0} profile created".format(profile_name)}
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
