from datetime import datetime
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from vendors.base import BaseDSLAM
from dj_bridge import DSLAM
from dj_bridge import DSLAMPort
from easysnmp import Session

class Huawei(BaseDSLAM):

    PORT_DETAILS_OID_TABLE = {
        "1.3.6.1.2.1.2.2.1.7"         : "PORT_ADMIN_STATUS",
        "1.3.6.1.2.1.2.2.1.8"         : "PORT_OPER_STATUS",
        "1.3.6.1.2.1.10.94.1.1.1.1.4" : "LINE_PROFILE",
        "1.3.6.1.2.1.10.94.1.1.2.1.4" : "ADSL_UPSTREAM_SNR",
        "1.3.6.1.2.1.10.94.1.1.2.1.5" : "ADSL_UPSTREAM_ATTEN",
        "1.3.6.1.2.1.10.94.1.1.2.1.8" : "ADSL_UPSTREAM_ATT_RATE",
        "1.3.6.1.2.1.10.94.1.1.5.1.2" : "ADSL_CURR_UPSTREAM_RATE",
        "1.3.6.1.2.1.10.94.1.1.3.1.4" : "ADSL_DOWNSTREAM_SNR",
        "1.3.6.1.2.1.10.94.1.1.3.1.5" : "ADSL_DOWNSTREAM_ATTEN",
        "1.3.6.1.2.1.10.94.1.1.3.1.8" : "ADSL_DOWNSTREAM_ATT_RATE",
        "1.3.6.1.2.1.10.94.1.1.4.1.2" : "ADSL_CURR_DOWNSTREAM_RATE",
    }
    PORT_DETAILS_OID_TABLE_INVERSE = {v:k for k, v in PORT_DETAILS_OID_TABLE.items()}

    PORT_ADMIN_STATUS = {1:"UNLOCK", 2:"LOCK", 3:"TESTING"}
    PORT_ADMIN_STATUS_INVERSE = {v:k for k, v in PORT_ADMIN_STATUS.items()}

    PORT_OPER_STATUS = {1:"SYNC", 2:"NO-SYNC", 3:"TESTING",
                        4:"UNKNOWN", 5:"DORMANT", 6:"NOT-PRESENT",
                        7:"LOWER-LAYER-DOWN", 65536:"NO-SYNC-GENERAL"}
    PORT_OPER_STATUS_INVERSE = {v:k for k, v in PORT_OPER_STATUS.items()}

    PORT_INDEX_TO_PORT_NAME_OID = '1.3.6.1.2.1.31.1.1.1.1'

    @classmethod
    def translate_admin_status_by_text(cls, admin_status):
        admin_status = admin_status.upper()
        if admin_status in cls.PORT_ADMIN_STATUS_INVERSE:
            return cls.PORT_ADMIN_STATUS_INVERSE[admin_status]
        return None

    @classmethod
    def translate_admin_status_by_value(cls, admin_status_val):
        if admin_status_val in cls.PORT_ADMIN_STATUS:
            return cls.PORT_ADMIN_STATUS[admin_status_val]
        return 'UNKNOWN'

    @classmethod
    def get_port_index_mapping(cls, dslam_info):
        """
        Get Port-Index to Port-Name mapping
        """
        port_index_mapping = []
        dslam_ip = dslam_info['ip']
        snmp_community = dslam_info['snmp_community']
        session = Session(hostname=dslam_ip, community=snmp_community, remote_port=snmp_port,timeout=snmp_timeout, retries=3,version=2)
        '''cmd_gen = cmdgen.CommandGenerator()
        error_indication, error_status,\
            error_index, var_binds = cmd_gen.nextCmd(
                cmdgen.CommunityData(snmp_community),
                cmdgen.UdpTransportTarget((dslam_ip, 161), timeout=3, retries=0),
                cls.PORT_INDEX_TO_PORT_NAME_OID)
        # Check for errors and print out results
        if error_indication:
            raise Exception(error_indication)
        else:
            if error_status:
                raise Exception('%s at %s' % (
                    error_status.prettyPrint(),
                    error_index and var_binds[int(error_index)-1][0] or '?'
                ))
            else:
                for row in var_binds:
                    for name, val in row:
                        port_idx = name.prettyPrint().split(".")[-1]
                        port_name = val.prettyPrint()
                        port_index_mapping.append((port_name, port_idx))
        '''

        var_binds = session.walk(cls.PORT_INDEX_TO_PORT_NAME_OID)
        for item in var_binds:
            port_index_mapping.append((item.oid_index, item.value))

        return port_index_mapping

    @classmethod
    def get_current_port_status(cls, dslam_info, port_index):
        port_current_status = {}
        snmp_community = dslam_info['snmp_community']
        dslam_ip = dslam_info['dslam_ip']
        session = Session(hostname=dslam_ip, community=snmp_community, remote_port=snmp_port,timeout=snmp_timeout, retries=3,version=2)
		#cmd_gen = cmdgen.CommandGenerator()
        for oid, item_name in cls.PORT_DETAILS_OID_TABLE.items():
            '''error_indication, error_status,\
                error_index, var_bind_table = cmd_gen.getCmd(
                    cmdgen.CommunityData(snmp_community),
                    cmdgen.UdpTransportTarget((dslam_ip, 161)),
                    oid+".%s" % port_index
                )
            if error_indication:
                raise Exception(error_indication)
            else:
                if error_status:
                    raise Exception('%s at %s' % (
                        error_status.prettyPrint(),
                        error_index and var_bind_table[-1][int(error_index)-1] or '?'
                    ))

                else:
                    for name, val in var_bind_table:
                        port_current_status[ item_name ] = val.prettyPrint()
            '''
            var_bind = session.get(oid+".{0}".format(port_index))
            if item_name == 'PORT_ADMIN_STATUS':
                value = cls.translate_admin_status_by_value(var_bind.value)
            elif item_name == 'PORT_OPER_STATUS':
                value = cls.translate_oper_status_by_value(var_bind.value)
            else:
                value = var_bind.value

            if 'No Such' in value: # Ignore this item since we have no data
                continue

            print('*************************************', value)
            port_current_status[ item_name ] = value



        port_current_status['fetched_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return port_current_status

    @classmethod
    def get_current_port_status_bulk(cls, dslam_info, dslam_port_map):
        snmp_community = dslam_info['snmp_community']
        dslam_ip = dslam_info['dslam_ip']
        #dslam_port_map = cls._get_all_port_mappings(dslam)
        port_mapping_len = len(dslam_port_map)
        ports_status = {}
        cmd_gen = cmdgen.CommandGenerator()
        oid_list = [
            #cls.PORT_DETAILS_OID_TABLE_INVERSE['PORT_ADMIN_STATUS'],
            #cls.PORT_DETAILS_OID_TABLE_INVERSE['PORT_OPER_STATUS'],
            cls.PORT_DETAILS_OID_TABLE_INVERSE['ADSL_DOWNSTREAM_SNR'],
            cls.PORT_DETAILS_OID_TABLE_INVERSE['ADSL_UPSTREAM_SNR']
        ]

        #session = Session(hostname=dslam_ip, community=snmp_community, remote_port=snmp_port,timeout=snmp_timeout, retries=3,version=2)
        #var_bind_table = session.get_bulk(*oid_list,0,port_mapping_len)

        error_indication, error_status,\
            error_index, var_bind_table = cmd_gen.bulkCmd(
                cmdgen.CommunityData(snmp_community),
                cmdgen.UdpTransportTarget((dslam_ip, 161), timeout=20),
                0, port_mapping_len, *oid_list
            )

        if error_indication:
            raise Exception(error_indication)
        else:
            if error_status:
                raise Exception('%s at %s' % (
                    error_status.prettyPrint(),
                    error_index and var_bind_table[-1][int(error_index)-1] or '?'
                ))

            else:
                for row in var_bind_table:
                    for oid, val in row:
                        oid, port_index = cls._resolve_oid(oid.prettyPrint())
                        port_name = dslam_port_map[port_index]
                        item_name = cls.PORT_DETAILS_OID_TABLE[oid]
                        if port_name not in ports_status:
                            ports_status[port_name] = {}
                        ports_status[port_name][item_name] = val.prettyPrint()
                        ports_status[port_name][
                            'fetched_at'
                        ] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return ports_status

    @classmethod
    def _resolve_oid(cls, oid):
        """
        Given an OID, return the parent OID part and Port-Index
        """
        oid = oid.split('.')
        port_index = oid[-1]
        oid = '.'.join(oid[:-1])
        return oid, port_index

    #@classmethod
    #def _get_all_port_mappings(cls, dslam):
    #    dslam_port_mappings = db_session.query(
    #        DSLAMPortMap
    #    ).filter(
    #        DSLAMPortMap.dslam_id==dslam.id
    #    ).all()
    #    port_map = {}
    #    for item in dslam_port_mappings:
    #        port_map[item.port_index] = item.port_name
    #    return port_map

    @classmethod
    def change_port_admin_status(cls, dslam_info, port_index, admin_status):
        #port_index = cls.resolve_port_name(dslam, port_name)
        admin_status = cls.translate_admin_status_by_text(admin_status)
        snmp_community = dslam_info['snmp_community']
        dslam_ip = dslam_info['dslam_ip']

        if admin_status is None:
            raise Exception('Invalid Admin Status Value')

        #session = Session(hostname=dslam_ip, community=snmp_community, remote_port=snmp_port,timeout=snmp_timeout, retries=3,version=2)
        #var_binds = session.set('.1.3.6.1.2.1.2.2.1.7.%s'%port_index,admin_status)

        cmd_gen = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_gen.setCmd(
            cmdgen.CommunityData(snmp_community),
            cmdgen.UdpTransportTarget((dslam_ip, 161), timeout=5, retries=2),
            ('.1.3.6.1.2.1.2.2.1.7.%s'%port_index, rfc1902.Integer(admin_status))
        )

        # Check for errors and print out results
        if error_indication:
            raise Exception(error_indication)
        else:
            if error_status:
                Exception('%s at %s' % (
                    error_status.prettyPrint(),
                    error_index and var_binds[int(error_index)-1][0] or '?'
                ))

        return True
