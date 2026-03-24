import os
import shutil
from colorama import Fore, Back, Style


def generate_krb5(domain, dc_ip):
    realm = domain.upper()
    print(f"[+] Configuring for DC: {dc_ip} ({domain})")

    krb5_conf = f"""
default_realm = {realm}
dns_lookup_realm = false
dns_lookup_kdc = false
ticket_lifetime = 24h
forwardable = true
rdns = false

[libdefaults]
    default_realm = {realm}
    dns_lookup_kdc = false
    dns_lookup_realm = false

[realms]
    {realm} = {{
        kdc = {dc_ip}
        admin_server = {dc_ip}
    }}

[domain_realm]
    .{domain} = {realm}
    {domain} = {realm}
"""

    print("\n[+] Generated krb5.conf:\n")
    print(krb5_conf)
    choice = input("Accept change? (Y/N) ").lower()

    if choice == "y":
        if os.geteuid() == 0:
            try:
                with open("/etc/krb5.conf", "w") as f:
                    f.write(krb5_conf)
                print("[+] /etc/krb5.conf updated")
            except Exception as e:
                print(f"[-] Failed to write krb5.conf: {e}")
        else:
            print("[!] Not running as root → cannot write /etc/krb5.conf")
    elif choice == "N":
        print("/etc/krb5.conf not updated")
        return
    else:
        print("Invalid option")
        print("/etc/krb5.conf not updated")
        return


def generate_etc_hosts(ip, hostname, dc=False):
    path = "/etc/hosts"
    entry = ""

    if dc:
        entry = f"{ip}  dc01.{hostname} {hostname}\n"
    else:
        entry = f"{ip}  {hostname}\n"

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        return {"success": False, "error": str(e)}

    entry_exists = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        parts = stripped.split()

        if parts[0] == ip or hostname in parts[1:]:
            entry_exists = True
            print(Fore.RED + Style.BRIGHT + f"[!] Existing entry found: {stripped}")
            print(Style.RESET_ALL)

            choice = input("[?] Overwrite this entry? (y/N): ").lower()
            if choice == "y":
                new_lines.append(entry)
                print(f"[+] Updated entry → {entry}")
            else:
                new_lines.append(line)
                print("[*] Keeping existing entry")
            
        else:
            new_lines.append(line)

    if not entry_exists:
        new_lines.append(f"\n{entry}\n")
        print(f"[+] Added new entry → {entry}")

    if os.geteuid() != 0:
        return {
            "success": False,
            "error": "Not root",
            "suggested": f"{entry}"
        }

    try:
        shutil.copy(path, path + ".bak")
        print(f"Generating backup in {path}.bak")
        with open(path, "w") as f:
            f.writelines(new_lines)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def add_vhost(target, domain, subdomains):
    path = "/etc/hosts"

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        return {"success": False, "error": str(e)}

    entry = f"{target} {domain} "
    for sub in subdomains:
        entry += f"{sub}"

    entry += "\n"

    print(f"[+] New /etc/hosts entry: {entry.strip()}")

    updated = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        parts = stripped.split()

        if parts[0] == target:
            new_lines.append(entry)
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(entry)

    try:
        with open(path, "w") as f:
            f.writelines(new_lines)
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {"success": True}


    