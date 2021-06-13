from .command_factory import CommandFactory

from .RB951Ui2HnD_commands.export_verbose_terse import Export_Verbose_Terse


class RB951Ui2HnD:
    command_factory = CommandFactory()
    command_factory.register_type('export verbose terse', Export_Verbose_Terse)

    def __init__(self):
        pass

    @classmethod
    def execute_command(cls, router_data, command, params):
        switch_id = router_data['id']
        switch_name = router_data['name']
        switch_ip = router_data['ip']
        switch_fqdn = router_data['fqdn']
        switch_type = router_data['switch_type']
        command_class = cls.command_factory.get_type(command)(params)
        return command_class.run_command()
