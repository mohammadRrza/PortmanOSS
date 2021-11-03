from .command_factory import CommandFactory

from .RB951Ui2HnD_commands.export_verbose_terse import ExportVerboseTerse
from .RB951Ui2HnD_commands.apply_permission import ApplyPermission
from .RB951Ui2HnD_commands.set_ssl_on_router import SetSSLOnRouter


class RB951Ui2HnD:
    command_factory = CommandFactory()
    command_factory.register_type('get Backup', ExportVerboseTerse)
    command_factory.register_type('apply permission', ApplyPermission)
    command_factory.register_type('set SSL on router', SetSSLOnRouter)

    def __init__(self):
        pass

    @classmethod
    def execute_command(cls, router_data, command, params):
        params['router_id'] = router_data['id']
        params['router_name'] = router_data['name']
        params['router_ip'] = router_data['ip']
        params['router_fqdn'] = router_data['fqdn']
        params['router_type'] = router_data['router_type']
        params['SSH_username'] = router_data['SSH_username']
        params['SSH_password'] = router_data['SSH_password']
        params['SSH_port'] = router_data['SSH_port']
        params['SSH_timeout'] = router_data['SSH_timeout']

        command_class = cls.command_factory.get_type(command)(params)
        return command_class.run_command()
