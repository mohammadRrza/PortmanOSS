from netmiko import ConnectHandler


class C2960:
    def __init__(self):
        pass

    def run_command(self):
        device = ConnectHandler(device_type='extreme_vdx', ip='172.19.177.254', username='taherabadi',
                                password='t@h3r68')
        output = device.send_command("show dot1x")
        print('dssdds')
