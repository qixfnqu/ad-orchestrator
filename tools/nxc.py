import subprocess
from core.config import NXC_SERVICE_MAP
from colorama import Fore, Back, Style
from core import aux
import re


<<<<<<< HEAD
import re

import re

=======
>>>>>>> 49bd065 (Refactor some functionality to native impacket library)
def parse_smb_enum(output):
    shares = []
    users = []
    in_shares = False
    in_users = False

    for line in output.splitlines():
        if "SMB" not in line:
            continue

        match = re.split(r"SMB\s+\S+\s+\d+\s+\S+\s+", line, maxsplit=1)
        if len(match) < 2:
            continue

        content = match[1].strip()
        if not content:
            continue

      
        if "[*] Enumerated shares" in content:
            in_shares = True
            in_users = False
            continue

       
        if content.startswith("-Username-"):
            in_shares = False
            in_users = True
            continue

       
        if content.startswith("[*] Enumerated") and "users" in content.lower():
            in_users = False
            continue

        # -------------------
        # PARSE SHARES
        # -------------------
        if in_shares:
            # ignorar headers
            if content.startswith("Share") or content.startswith("-----"):
                continue

            parts = re.split(r"\s{2,}", content)
            if parts and parts[0]:
                shares.append(parts[0].strip())

        # -------------------
        # PARSE USERS
        # -------------------
        elif in_users:
            parts = re.split(r"\s{2,}", content)
            if parts and parts[0]:
                users.append(parts[0].strip())

    # eliminar duplicados manteniendo orden
    shares = list(dict.fromkeys(shares))
    users = list(dict.fromkeys(users))

    print(Fore.GREEN + f"[+] Found {len(shares)} shares" + Style.RESET_ALL)
    print(Fore.GREEN + f"[+] Found {len(users)} users" + Style.RESET_ALL)

    return {
        "shares": shares,
        "users": users
    }


def check_null_session(target):
    cmd = ["nxc", "smb", target, "-u", "", "-p", ""]

    output = aux.run_command(cmd)

    keywords = [
        "Pwn3d",
        "STATUS_SUCCESS",
        "Null Auth:True",
        "Guest session"
    ]

    for k in keywords:
        if k in output:
            return True

    return False


def smb_enum(target, username="", password=""):

    cmd = [
        "nxc", "smb", target,
        "-u", username,
        "-p", password,
        "--shares",
        "--users",
        "--pass-pol",
        "--rid-brute"
    ]

    output = aux.run_command(cmd)

    if "STATUS_ACCESS_DENIED" in output:
        return False

    return parse_smb_enum(output)


def get_nxc_modules(ports):
    modules = set()

    for p in ports:
        if p in NXC_SERVICE_MAP:
            modules.add(NXC_SERVICE_MAP[p])

    return list(modules)

def test_access(target, ports, username="", password=""):
    services_with_access = []
    modules = get_nxc_modules(ports)

    for module in modules:
        cmd = [
            "nxc", module, target,
            "-u", username,
            "-p", password
        ]

        output = aux.run_command(cmd)

        keywords = [
        "Pwn3d",
        "STATUS_SUCCESS",
        "[+]"
        ]

        success = False
        for k in keywords:
            if k in output:
                success = True
                services_with_access.append({module : (username, password)})
                print(Fore.GREEN + Style.BRIGHT + f"[+] User {username} has access to {module} with password {password}" + Style.RESET_ALL)
                break

        if success == False:
            cmd = [
                "nxc", module, target,
                "-u", username,
                "-p", password,
                "--local-auth"
            ]

            output = aux.run_command(cmd)

            keywords = [
            "Pwn3d",
            "STATUS_SUCCESS",
            "[+]"
            ]

            for k in keywords:
                if k in output:
                    services_with_access.append({module : (username, password)})
                    print(Fore.GREEN + f"[+] User {username} has access to {module}" + Style.RESET_ALL)
                    break

    return services_with_access
