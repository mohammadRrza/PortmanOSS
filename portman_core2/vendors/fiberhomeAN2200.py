import time
from vendors.base import BaseDSLAM
import telnetlib
import jsonrpclib
from command_factory import CommandFactory
from fiberhomeAN2200_commands.ShowCard import ShowCard
from fiberhomeAN2200_commands.Version import Version
from fiberhomeAN2200_commands.ShowShelf import ShowShelf


class FiberhomeAN2200(BaseDSLAM):
    command_factory = CommandFactory()
    command_factory.register_type('Show Card', ShowCard)
    command_factory.register_type('Version', Version)

    EVENT = {'dslam_connection_error':'DSLAM Connection Error', 'no_such_object':'No Such Objects'}
    EVENT_INVERS = dict(zip(EVENT.values(),EVENT.keys()))

    PORT_ADMIN_STATUS = {1:"UNLOCK", 2:"LOCK", 3:"TESTING"}
    PORT_ADMIN_STATUS_INVERSE = {v:k for k, v in PORT_ADMIN_STATUS.iteritems()}

    PORT_OPER_STATUS = {1:"SYNC", 2:"NO-SYNC", 3:"TESTING",
                        4:"UNKNOWN", 5:"DORMANT", 6:"NOT-PRESENT",
                        7:"LOWER-LAYER-DOWN", 65536:"NO-SYNC-GENERAL"}
    PORT_OPER_STATUS_INVERSE = {v:k for k, v in PORT_OPER_STATUS.iteritems()}

    @classmethod
    def translate_event_by_text(cls, event):
        if event in cls.EVENT_INVERS:
            return cls.EVENT_INVERS[event]
        return None

    @classmethod
    def translate_admin_status_by_text(cls, admin_status):
        admin_status = admin_status.upper()
        if admin_status in cls.PORT_ADMIN_STATUS_INVERSE:
            return cls.PORT_ADMIN_STATUS_INVERSE[admin_status]
        return None

    @classmethod
    def translate_admin_status_by_value(cls, admin_status_val):
        if not admin_status_val.isdigit():
            return admin_status_val

        admin_status_val = int(admin_status_val)
        if admin_status_val in cls.PORT_ADMIN_STATUS:
            return cls.PORT_ADMIN_STATUS[admin_status_val]
        return admin_status_val

    @classmethod
    def translate_oper_status_by_value(cls, oper_status_val):
        if not oper_status_val.isdigit():
            return oper_status_val

        oper_status_val = int(oper_status_val)
        if oper_status_val in cls.PORT_OPER_STATUS:
            return cls.PORT_OPER_STATUS[oper_status_val]
        return oper_status_val

    @classmethod
    def get_current_port_status(cls, dslam_data, slot_number, port_number, port_index):
        params = {
                'dslam_id': dslam_data.get('id'),
                'slot_number': slot_number,
                'port_number': port_number
                }
        command = 'get current port status'
        c = jsonrpclib.Server('http://127.0.0.1:7090')
        return c.telnet_run_command(dslam_data.get('id'), command, params)




    @classmethod
    def get_ports_status(cls, dslam_info, request_q):
        print '++++++++++++++++++++++++++++'
        print 'send request'
        print '++++++++++++++++++++++++++++'
        request_q.put((dslam_info.get('id'), 'get ports status', {'dslam_id': dslam_info.get('id'), 'slots': dslam_info.get('slot_count')}))

    @classmethod
    def get_port_vpi_vci(cls, dslam_info, request_q):
        print '++++++++++++++++++++++++++++'
        print 'send request get vpi vci'
        print '++++++++++++++++++++++++++++'
        request_q.put((dslam_info.get('id'), 'get ports vpi vci', {'dslam_id': dslam_info.get('id')}))

    @classmethod
    def get_atten_flag(cls, atten_value):
        if atten_value <= 20:
            return 'outstanding'
        elif atten_value > 20  and atten_value <= 30 :
            return 'excellent'
        elif atten_value > 30 and atten_value <= 40 :
            return 'very_good'
        elif atten_value > 40 and atten_value <= 50 :
            return 'good'
        elif atten_value > 50 and atten_value <= 60 :
            return 'poor'
        else:
            return 'bad'


    @classmethod
    def get_snr_flag(cls, snr_value):
        if snr_value <= 6:
            return 'bad'
        elif snr_value > 6  and snr_value <= 10 :
            return 'fair'
        elif snr_value > 10 and snr_value <= 20 :
            return 'good'
        elif snr_value > 20 and snr_value <= 29 :
            return 'excellent'
        else:
            return 'outstanding'


    @classmethod
    def execute_command(cls, dslam_info, command, params):
        params['set_snmp_community'] = dslam_info['set_snmp_community']
        params['get_snmp_community'] = dslam_info['get_snmp_community']
        params['snmp_port'] = dslam_info['snmp_port']
        params['snmp_timeout'] = dslam_info['snmp_timeout']
        command_class = cls.command_factory.get_type(command)(params)
        command_class.HOST = dslam_info['ip']
        command_class.telnet_username = dslam_info['telnet_username']
        command_class.telnet_password = dslam_info['telnet_password']
        return command_class.run_command()
    @classmethod
    def execute_bulk_command(cls, task, result_filepath, success_filepath, error_filepath):
        for dslam_data in task.dslams_data:
            ip = dslam_data.get('ip')
            telnet_username = dslam_data.get('telnet_username')
            telnet_password = dslam_data.get('telnet_password')
            result = Zyxel.run_commands(ip, telnet_username,telnet_password, task.commands)
            print '*****************************************'
            print result
            print '*****************************************'
            if result:
                with open(result_filepath, 'ab') as log_file:
                    log_file.write('\r\n\r\n=======================================\r\n\r\n')
                    log_file.write('\r\n\r\nid: {0}, name: {1}, ip: {2}\r\n\r\n'.format(dslam_data.get('id'), dslam_data.get('name').encode('utf-8'), dslam_data.get('ip')))
                    log_file.write(result+'\n')
                    log_file.write('\r\n\r\n=======================================\r\n\r\r\n')
                with open(success_filepath, 'ab') as success_file:
                    success_file.write(str(dslam_data.get('id'))+','+dslam_data.get('ip')+'\n')
            else:
                with open(error_filepath, 'ab') as error_file:
                    error_file.write(str(dslam_data.get('id'))+','+dslam_data.get('ip')+'\n')
        return {'result': 'run dslam bulk command is done'}


    @classmethod
    def run_commands(cls, HOST, user, password, commands):
        try:
            tn = telnetlib.Telnet(HOST)
            tn.write((user + "\r\n").encode('utf-8'))
            tn.write((password + "\r\n").encode('utf-8'))
            time.sleep(1)
            result = tn.read_until('Password:')
            for command in commands:
                tn.write("{0}\r\n\r\n".format(command))
                time.sleep(1)
            tn.write("end\r\n")
            result = tn.read_until('end')
            tn.write("exit\r\n")
            tn.write("y\r\n")
            tn.close()
            results = result.split('\n')
            results = '\n'.join(results[3:len(results)-4])
            return results
        except Exception as ex:
            print '---------------------'
            print ex
            print HOST+','+user+','+password
            print '---------------------'
            return None
