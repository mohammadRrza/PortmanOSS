import ldap

LDAP_SERVER = 'ldap://172.28.238.238:389'
LDAP_BASE = "DC=pishgaman,DC=local"


def ldap_auth(username, password):
    conn = ldap.initialize(LDAP_SERVER)
    try:
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(username, password)
        logon_name = conn.whoami_s().split('\\')[1]
        search_filter = f"(sAMAccountName={logon_name})"
        retrieve_attributes = ['memberOf']
        search_res = conn.search_s(LDAP_BASE, ldap.SCOPE_SUBTREE, search_filter, retrieve_attributes)
        group_info = search_res[0][1]
        if isinstance(group_info, dict):
            info = group_info.get('memberOf')
        res = [str(i).replace('b', '').replace("'", "") for i in info]
        group_name = str(res[1]).split(",")[0].split("=")[1]

    except ldap.LDAPError as e:
        return f'failed to authenticate'

    conn.unbind_s()
    return dict(message="Success", group_name=group_name, logon_name=logon_name)


if __name__ == "__main__":
    user = ldap_auth('1741298148@pishgaman.local', 'Saida@71@')
    print(user)
