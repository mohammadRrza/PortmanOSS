
-------------------------router-------------------------------------------------
ALTER SEQUENCE router_router_id_seq RESTART WITH 323;
DELETE FROM router_router;
INSERT INTO "public"."router_router"("device_interfaceid", "host_id", "device_name", "device_ip", "device_fqdn", "router_brand_id", "router_type_id","SSH_password", "SSH_username", "SSH_port", "SSH_timeout", "last_update")
 SELECT DISTINCT 1 as device_interfaceid,zabbix_hosts.host_id,'' as device_name,zabbix_hosts.device_ip,zabbix_hosts.device_fqdn, router_routergroup.router_brand_id,router_routergroup."id",'eS7*XiMmyeeU'as SSH_password,'mik-backup' as SSH_username, 1001 as SSH_port, 5 as SSH_timeout, NOW() from zabbix_hosts
  LEFT JOIN router_routergroup on router_routergroup.title = zabbix_hosts.device_type
	where (zabbix_hosts.device_fqdn like '%rou%' or zabbix_hosts.device_fqdn like '%core%' or zabbix_hosts.device_type = 'router_board' or zabbix_hosts.device_type = 'router_virtual') and router_routergroup.title is not NULL and device_fqdn not like '%OLD%'	ORDER BY zabbix_hosts.device_ip;
-------------------------router-------------------------------------------------


-------------------------switch-------------------------------------------------
 ALTER SEQUENCE switch_switch_id_seq RESTART WITH 123;
 DELETE from switch_switch;
 INSERT INTO "public"."switch_switch"( "device_interfaceid", "host_id", "device_name", "device_ip", "device_fqdn", "Switch_brand_id", "Switch_type_id", "SSH_password", "SSH_username", "SSH_port", "SSH_timeout","last_update")
 SELECT DISTINCT 2 as device_interfaceid,zabbix_hosts.host_id,'' as device_name,zabbix_hosts.device_ip,zabbix_hosts.device_fqdn, switch_switchgroup.switch_brand_id,switch_switchgroup."id",'Yq*teoyg&fb@'as SSH_password,'backup-noc' as SSH_username, 22 as SSH_port, 5 as SSH_timeout , NOW() from zabbix_hosts
  LEFT JOIN switch_switchgroup on switch_switchgroup.title = zabbix_hosts.device_type
where zabbix_hosts.device_fqdn like '%swi%' and switch_switchgroup.title is not NULL and device_fqdn not like '%OLD%' ORDER BY zabbix_hosts.device_ip;

INSERT INTO "public"."switch_switch"( "device_interfaceid", "host_id", "device_name", "device_ip", "device_fqdn", "Switch_brand_id", "Switch_type_id", "SSH_password", "SSH_username", "SSH_port", "SSH_timeout","last_update")
 SELECT DISTINCT 2 as device_interfaceid,zabbix_hosts.host_id,'' as device_name,zabbix_hosts.device_ip,zabbix_hosts.device_fqdn, switch_switchgroup.switch_brand_id,switch_switchgroup."id",'Yq*teoyg&fb@'as SSH_password,'backup-noc' as SSH_username, 22 as SSH_port, 5 as SSH_timeout, NOW() from zabbix_hosts
  LEFT JOIN switch_switchgroup on switch_switchgroup.title = zabbix_hosts.device_type
where switch_switchgroup.title is not NULL and device_fqdn not like '%OLD%' and device_type = 'switch_layer3' ORDER BY zabbix_hosts.device_ip;
-------------------------switch-------------------------------------------------


-------------------------radio-------------------------------------------------
 ALTER SEQUENCE radio_radio_id_seq RESTART WITH 123;
 DELETE from radio_radio;
 INSERT INTO "public"."radio_radio"( "device_interfaceid", "host_id", "device_name", "device_ip", "device_fqdn", "radio_brand_id", "radio_type_id", "SSH_password", "SSH_username", "SSH_port", "SSH_timeout")
 SELECT DISTINCT 3 as device_interfaceid,zabbix_hosts.host_id,'' as device_name,zabbix_hosts.device_ip,zabbix_hosts.device_fqdn, radio_radiogroup.radio_brand_id,radio_radiogroup."id",'eS7*XiMmyeeU'as SSH_password,'mik-backup' as SSH_username, 22 as SSH_port, 5 as SSH_timeout from zabbix_hosts
  LEFT JOIN radio_radiogroup on radio_radiogroup.title = zabbix_hosts.device_type
	where radio_radiogroup.title is not NULL and device_fqdn not like '%OLD%'	ORDER BY zabbix_hosts.device_ip;
-------------------------radio-------------------------------------------------

-------------------------portman_zabbix_hosts-------------------------------------------------
ALTER SEQUENCE portman_zabbix_hosts_id_seq RESTART WITH 2526;

DELETE FROM portman_zabbix_hosts;

INSERT INTO "public"."portman_zabbix_hosts"("host_id", "device_group", "device_ip", "device_fqdn", "last_updated", "device_type", "device_brand")

select "host_id", "device_group", "device_ip", "device_fqdn", "last_updated", "device_type", "device_brand" from zabbix_hosts;
-------------------------portman_zabbix_hosts-------------------------------------------------