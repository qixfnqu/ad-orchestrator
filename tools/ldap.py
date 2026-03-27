<<<<<<< HEAD
import subprocess
from core import aux

=======
>>>>>>> 49bd065 (Refactor some functionality to native impacket library)
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

from colorama import Fore, Back, Style

def anon_bind(target, ports):
    for port in ports:
<<<<<<< HEAD
        print(f"[+] Trying on port {port}")

        cmd = [
            "ldapsearch",
            "-x",
            "-H", f"ldap://{target}:{port}",
            "-s", "base",
            "(objectclass=*)"
        ]

        output = aux.run_command(cmd)

        if "Can't contact LDAP server" not in output:
            return output
=======
        print(f"[*] Testing anonymous bind on {target}:{port}...")
        try:
            server = Server(f'ldap://{target}:{port}', get_info=ALL, connect_timeout=5)
            
            conn = Connection(server, auto_bind=True, raise_exceptions=True)
            
            print(Fore.GREEN + f"[+] Success! Anonymous bind allowed on port {port}" + Style.RESET_ALL)

            dse_info = server.info.naming_contexts
            domain_name = server.info.other.get('defaultNamingContext', ['Not found'])[0]
            
            print(f"    - Naming Contexts: {', '.join(dse_info)}")
            print(f"    - Default Context: {domain_name}")

            return {
                "port": port,
                "contexts": dse_info,
                "default_dn": domain_name,
                "raw_info": str(server.info)
            }

        except LDAPException:
            print(Fore.RED + f"[-] Anonymous bind failed on port {port}" + Style.RESET_ALL)
            continue
            
        finally:
            if 'conn' in locals() and conn.bound:
                conn.unbind()
>>>>>>> 49bd065 (Refactor some functionality to native impacket library)

    return None

def cred_bind(target, ports, username, password, domain):
    print(f"[+] Trying to enumerate users and computers")

    base_dn = f"DC={domain.upper().replace('.', ',DC=')}"

    attrs = [
        'distinguishedName', 
        'sAMAccountName', 
        'userPrincipalName', 
        'servicePrincipalName', 
        'userAccountControl', 
        'memberOf', 
        'msDS-AllowedToDelegateTo'
    ]


    for port in ports:
        try:
            print(f"[+] Trying on port {port}")

            server = Server(f'ldap://{target}:{port}', get_info=ALL, connect_timeout=5)

            conn = Connection(
                    server, 
                    user=f"{username}@{domain}", 
                    password=password, 
                    auto_bind=True,
                    raise_exceptions=True
                )

            #Search Users
            search_filter = "(|(objectClass=user))"

            conn.search(
                    search_base=base_dn,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=attrs
                )

            print(Fore.GREEN + f"[+] Found {len(conn.entries)} users." + Style.RESET_ALL)
            users = []
            for entry in conn.entries:
                users.append(str(entry.sAMAccountName.value))



            #Search Computers
            search_filter = "(|(objectClass=computer))"

            conn.search(
                    search_base=base_dn,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=attrs
                )

            print(Fore.GREEN + f"[+] Found {len(conn.entries)} computers." + Style.RESET_ALL)
            computers = []
            for entry in conn.entries:
                computers.append(str(entry.sAMAccountName.value))

            return (users, computers)

        except LDAPBindError:
            print(Fore.RED + "[-] LDAP bind error" + Style.RESET_ALL)
        except LDAPException as e:
            print(Fore.RED + f"[-] LDAP failed with {e}" + Style.RESET_ALL)
        finally:
            if 'conn' in locals() and conn.bound:
                conn.unbind()
            

    return ()