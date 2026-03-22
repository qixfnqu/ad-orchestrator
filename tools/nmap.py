import subprocess

def run_scan(cmd):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output = ""

    for line in process.stdout:
        print(line, end="")
        output += line

    process.wait()
    return output


def basic_scan(target, save=False):
    cmd = f"nmap -sC -sV {target}"

    if save:
        cmd += f" -oN {target}_scan.txt"

    return run_scan(cmd)


def extensive_scan(target,  save=False):
    cmd = (
        f"nmap -sUV -sC "
        f"-p 53,88,123,135,137,139,389,445,464,636,3268,3269 "
        f"--script=\"banner,ldap*,smb*,krb5*,msrpc*\" "
        f"--script-args \"ldap.show-all-info=true,unsafe=1\" "
        f"{target}"
    )

    if save:
        cmd += f" -oN {target}_scan.txt"

    return run_scan(cmd)

def kerberos_scan(target,realm, dict_path, save=False):
    cmd = f"nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='{realm}',krb5-enum-users.userdict={dict_path} {target}"

    if save:
        cmd += f" -oN {target}_kerberos_scan.txt"

    return run_scan(cmd)