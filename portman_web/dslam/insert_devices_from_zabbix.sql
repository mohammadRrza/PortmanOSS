INSERT INTO "public"."router_router"("device_interfaceid", "host_id", "device_name", "device_ip", "device_fqdn",
                                     "router_brand_id", "router_type_id", "SSH_password", "SSH_username", "SSH_port",
                                     "SSH_timeout")
SELECT DISTINCT 1    as device_interfaceid,
                zabbix_hosts.host_id,
                '''' as device_name,
                zabbix_hosts.device_ip,
                zabbix_hosts.device_fqdn,
                router_routergroup.router_brand_id,
                router_routergroup."id",
                ''      eS7*XiMmyeeU''as SSH_password,'' mik-backup'' as SSH_username, 1001 as SSH_port,
                5    as SSH_timeout
from zabbix_hosts
         LEFT JOIN router_routergroup on router_routergroup.title = zabbix_hosts.device_type
where zabbix_hosts.device_fqdn like ''%rou%'' and router_routergroup.title is not NULL and device_fqdn not like ''%OLD%''
ORDER BY zabbix_hosts.device_ip