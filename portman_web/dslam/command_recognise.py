def command_recognise(command):
    if command == 'show linerate' or command == 'showPort' or command == 'show port':
        command = 'show linerate'
    elif command == 'profile adsl show' or command == 'showProfiles' or command == 'showprofiles' or command == 'show profiles':
        command = 'profile adsl show'
    elif command == 'show profile by port' or command == 'Show Profile By Port':
        command = 'show profile by port'
    elif command == 'setPortProfiles' or command == 'Set Port Profiles' or command == 'profile adsl set' or command == 'setProfiles' or command == 'change lineprofile port':
        command = 'setPortProfiles'
    elif command == 'profile vdsl show' or command == 'showVdslProfiles' or command == 'Show VDSL':
        command = 'profile vdsl show'
    elif command == 'profile vdsl set' or command == 'setVdslProfiles' or command == 'Set VDSL':
        command = 'profile vdsl set'
    elif command == 'selt show' or command == 'show selt' or command == 'selt' or command == 'showSelt':
        command = 'showSelt'
    elif command == 'selt start' or command == 'Selt Start' or command == 'start selt' or command == 'startSelt':
        command = 'selt start'
    elif command == 'show lineinfo' or command == 'Show Lineinfo' or command == 'Show LineInfo':
        command = 'show lineinfo'
    elif command == 'show linestat port' or command == 'Show Linestat Port':
        command = 'show linestat port'

    elif command == 'open port' or command == 'port enable' or command == 'openPort':
        command = 'port enable'
    elif command == 'close port' or command == 'port disable':
        command = 'port disable'
    elif command == 'show mac slot port' or command == 'showmacslotport':
        command = 'show mac by slot port'
    elif command == 'show mac by slot' or command == 'showmacslot':
        command = 'show mac by slot'
    elif command == 'show port with mac' or command == 'show port mac':
        command = 'show port with mac'
    elif command == 'Show VLAN' or command == 'VLAN Show' or command == 'show vlan' or command == 'vlan show':
        command = 'Show VLAN'
    elif command == 'Show All VLANs' or command == 'All VLANs Show' or command == 'show all pvc vlans':
        command = 'Show All VLANs'
    elif command == 'add to vlan' or command == 'Add To Vlan' or command == 'add to VLAN':
        command = 'add to vlan'
    elif command == 'Show Service' or command == 'show service':
        command = 'show service'
    elif command == 'Show Shelf' or command == 'show shelf':
        command = 'Show Shelf'
    elif command == 'Show Card' or command == 'show card':
        command = 'Show Card'
    elif command == 'Show Card Range' or command == 'show card range':
        command = 'Show Card Range'
    elif command == 'port reset' or command == 'reset port':
        command = 'port reset'
    elif command == 'save config' or command == 'Save Config' or command == 'config save':
        command = 'save config'
    elif command == 'ip show' or command == 'show ip' or command == 'IP Show':
        command = 'IP Show'
    elif command == 'ip arp show' or command == 'IP ARP Show':
        command = 'ip arp show'
    elif command == 'show snmp community' or command == 'sys snmp show' or command == 'snmp show':
        command = 'show snmp community'
    elif command == 'show time' or command == 'show uptime' or command == 'Show UpTime':
        command = 'show time'
    elif command == 'show mac' or command == 'Show MAC':
        command = 'show mac'
    elif command == 'show temp' or command == 'Show Temp' or command == 'Show Temperature':
        command = 'show temp'
    elif command == 'version' or command == 'Version' or command == 'Show version':
        command = 'Version'
    elif command == 'show pvc' or command == 'Show PVC' or command == 'ShowPVC':
        command = 'show pvc'
    elif command == 'show pvc profile id' or command == 'Show PVC Profile ID':
        command = 'show pvc profile id'
    elif command == 'show pvc by profile' or command == 'Show PVC By Profile':
        command = 'show pvc by profile'
    elif command == 'show pvc by port' or command == 'Show PVC By Port' or command == 'show pvc by port' or command == 'port pvc show':
        command = 'show pvc by port'
    elif command == 'show mac limit' or command == 'ACL Maccount Show' or command == 'Show Mac Limit' or command == 'acl maccount Show':
        command = 'acl maccount show'
    elif command == 'switch port show' or command == 'Switch Port Show':
        command = 'switch port show'
    elif command == 'show profile by port' or command == 'showProfile by port':
        command = 'show profile by port'
    elif command == 'port Info' or command == 'port info' or command == 'Port Info':
        command = 'port Info'
    elif command == 'Sys Info Show' or command == 'sys info show' or command == 'SYS Info Show':
        command = 'sys info show'
    elif command == 'acl pktfilter show' or command == 'ACL Pktfilter Show' or command == 'Acl Pktfilter Show':
        command = 'acl pktfilter show'
    elif command == 'acl pppoeagent show' or command == 'ACL PPPoEAgent Show' or command == 'Acl Pppoeagent Show':
        command = 'acl pppoeagent show'
    elif command == 'ngn_register_port' or command == 'ngn register port' or command == 'NGN register port':
        command = 'ngn_register_port'
    elif command == 'sip_configuration' or command == 'sip configuration' or command == 'SIP Configuration':
        command = 'sip_configuration'
    elif command == 'assign_number_to_user' or command == 'assign number to user' or command == 'registerNumber':
        command = 'assign_number_to_user'
    elif command == 'adsl annexm enable' or command == 'ADSL Annexm Enable' or command == 'enable annexm' or command == 'Enable Annexm':
        command = 'enable annexm'
    elif command == 'adsl annexm disable' or command == 'ADSL Annexm Disable' or command == 'disable annexm' or command == 'Disable Annexm':
        command = 'disable annexm'
    elif command == 'adsl annexm show' or command == 'ADSL Annexm Show' or command == 'show annexm' or command == 'Show Annexm':
        command = 'show annexm'
    elif command == 'fast profiles adsl show' or command == 'showFastProfiles':
        command = 'fast profiles adsl show'
    elif command == 'fast profiles adsl set':
        command = 'fast profiles adsl set'

    return command