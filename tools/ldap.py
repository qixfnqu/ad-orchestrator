import subprocess

def anon_bind(target, ports):
    for port in ports:
        print(f"[+] Trying on port {port}")

        cmd = [
            "ldapsearch",
            "-x",
            "-H", f"ldap://{target}:{port}",
            "-s", "base",
            "(objectclass=*)"
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        output = ""

        for line in process.stdout:
            print(line, end="")
            output += line

        process.wait()

        if "Can't contact LDAP server" not in output:
            return output

    return None

def cred_bind(target, ports, username, password, domain):
    print(f"[+] Trying to enumerate users and computers")
    for port in ports:
        print(f"[+] Trying on port {port}")

        cmd = [
            "ldapsearch",
            "-x",
            "-H", f"ldap://{target}:{port}",
            "-D", f"{domain}\\{username}", 
            "-w", password,
            "-b", f"DC={domain.replace('.', ',DC=')}", 
            "(|(objectClass=user)(objectClass=computer))", 
            "distinguishedName,samAccountName,userPrincipalName,sPN,dontReqPreAuth,userAccountControl,memberOf,msDS-AllowedToDelegateTo"
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        output = ""

        for line in process.stdout:
            print(line, end="")
            output += line

        process.wait()

        if "Can't contact LDAP server" not in output:
            return output

    return None