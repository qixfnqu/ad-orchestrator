#!/usr/bin/env python3
from tools import nmap, nxc, rpc, kerbrute_enum, kerberoast, web_enum, ldap, smbclient, bloodhound_handler
from core import config_manager
from core.aux import get_services

import re
import time
from colorama import Fore, Style


# ----------------------
# Utility helpers
# ----------------------

def confirm(prompt):
    return input(prompt).lower() in ["", "y"]


def ask_skip(prompt):
    print("\n")
    return confirm(prompt)


def ensure_target(session):
    if not session.target:
        print(Fore.RED + "[-] No target set" + Style.RESET_ALL)
        return False

    if session.target not in session.data["hosts"]:
        session.data["hosts"].append(session.target)

    return True


# ----------------------
# Core logic
# ----------------------

def is_probable_dc(ports):
    services = get_services(ports)
    if not {"kerberos", "ldap"}.issubset(services):
        return False
    return any(s in services for s in ["smb", "rpc", "dns"])


def extract_domain(nmap_output):
    match = re.search(r"Domain:\s*([a-zA-Z0-9\.\-]+)", nmap_output)
    if match:
        return match.group(1).lower()

    match = re.search(r"Nmap scan report for .*?\.(\S+)", nmap_output)
    if match:
        parts = match.group(1).split(".")
        if len(parts) >= 3:
            return f"{parts[1]}.{parts[2]}".lower()
    return None


# ----------------------
# Steps
# ----------------------

def step_nmap(session):
    print("Choose nmap scan type:\n1) Basic\n2) Extensive")
    mode = input("> ").strip()
    save = confirm("Save results? (Y/N): ")

    if not confirm("Execute scan? (Y/N): "):
        return

    if mode == "2":
        output = nmap.extensive_scan(session.target, save)
    else:
        output = nmap.basic_scan(session.target, save)

    session.data["nmap_output"] = output[0]
    session.data["ports"] = output[1]
    session.data["services"] = get_services(output[1])


def step_dc_setup(session):
    if not is_probable_dc(session.data.get("ports", [])) or session.dc_config:
        return

    print("[+] Target looks like a Domain Controller")

    if not confirm("Configure DC? (Y/N): "):
        return

    domain = session.domain or extract_domain(session.data.get("nmap_output", ""))
    if not domain:
        print(Fore.RED + "[-] Could not extract domain" + Style.RESET_ALL)
        return

    session.domain = domain
    config_manager.generate_krb5(domain, session.target)
    session.dc_config = True

    if confirm("Add /etc/hosts entry? (Y/N): "):
        config_manager.generate_etc_hosts(session.target, domain, True)


def step_ldap_anon(session):
    output = ldap.anon_bind(session.target, [389, 636, 3268, 3269])
    session.data["ldap_info"] = output

def step_ldap_cred(session):
    if not session.domain:
        setdomain = confirm("[-] No domain established. Do you want to set it manually? (Y/N) ")
        if setdomain:
            domain = input("Domain name: ").strip()
            session.domain = domain
        else:
            print(Fore.RED + "[-] Domain required for this step" + Style.RESET_ALL)
            return

    output = ldap.cred_bind(session.target, [389, 636, 3268, 3269], session.username, session.password, session.domain)
    session.data["ldap_info"] = output

def step_smb(session):
    if not nxc.check_null_session(session.target):
        print(Fore.RED + "[-] No anonymous SMB access" + Style.RESET_ALL)
        return

    session.data["smb_null_session"] = True

    output = nxc.smb_enum(session.target)
    if not output:
        session.data["smb_shares"] = smbclient.list_shares(session.target)


def step_rpc(session):
    if not rpc.anon_session(session.target):
        print(Fore.RED + "[-] RPC null session failed" + Style.RESET_ALL)


def step_kerbrute(session):
    if not session.domain:
        print(Fore.RED + "[-] No domain set" + Style.RESET_ALL)
        return

    wordlist = input("Wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip() or \
        "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"

    result = kerbrute_enum.user_enum(session.domain, session.target, wordlist)

    if result["users"]:
        session.data["users"] = list(set(session.data["users"] + result["users"]))


def step_kerberoast(session):
    if not session.domain:
        print(Fore.RED + "[-] No domain set" + Style.RESET_ALL)
        return

    wordlist = input("Wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip() or \
        "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"

    kerberoast.unauthenticated_asrep(session.target, session.domain, wordlist)
    kerberoast.unauthenticated_kerberoast(session.target, session.domain)


def step_web(session):
    use_https = "https" in session.data.get("services", [])

    if session.domain:
        add_entry = confirm("Do you want to add an /etc/hosts entry for the target? (Y/N) ")
        if add_entry:
            config_manager.generate_etc_hosts(session.target, session.domain)
    else:
        set_domain = confirm("Do you want to set a domain name for the target? (Y/N) ")
        if set_domain:
            domain = input("Domain name: ").lower().strip()
            session.domain = domain
        add_entry = confirm("Do you want to add an /etc/hosts entry for the target? (Y/N) ")
        if add_entry:
            config_manager.generate_etc_hosts(session.target, session.domain)

    scan_target = session.domain or session.target

    web_enum.basic_web_enum(scan_target, use_https)

    if confirm("Run Gobuster? (Y/N): "):
        wordlist = input("Wordlist (default=/usr/share/wordlists/dirb/common.txt): ").strip() or \
            "/usr/share/wordlists/dirb/common.txt"
        routes = web_enum.fuzz(scan_target, use_https, wordlist)
        session.data["routes"] = list(set(session.data["routes"] + routes))

    if confirm("Enumerate subdomains? (Y/N): "):
        mode = input("Choose mode (normal/vhost): ").strip()
        if mode != "normal" and mode != "vhost":
            mode = "normal"

        wordlist = input("Wordlist (default=/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt: ").strip() or \
            "/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt"
        subdomains = web_enum.subdomain_discovery(scan_target, session.domain, mode, wordlist, use_https)
        session.data["subdomains"] = list(set(session.data["subdomains"] + subdomains))

def step_bloodhound(session):
    if not session.domain:
        set_domain = confirm("[?] No domain set, do you want to manually set it? (Y/N) ")
        if set_domain:
            domain = input("Domain name: ").lower().strip()
            session.domain = domain
        else:
            print(Fore.RED + "[-] Domain required for bloodhound scan")
            return

    bloodhound_handler.bh_enum(session.target, session.domain, session.username, session.password)



# ----------------------
# Pipeline
# ----------------------

def run_step(name, should_skip, fn):
    print("\n" + Fore.CYAN + f"[ {name} ]" + Style.RESET_ALL + "\n")

    if should_skip:
        print("[*] Skipped\n")
        return

    fn()


def non_credentialed(session):
    if not ensure_target(session):
        return

    skip = False

    if session.data["nmap_output"]:
        skip = ask_skip("[?] Found nmap data in session. Do you want to skip this step? (Y/N) ")
    else:
        skip = ask_skip("[?] Nmap may take some time depending on scan type. Do you want to skip this step (no services will be discovered)? (Y/N) ") 

    run_step(
        "NMAP",
        skip,
        lambda: step_nmap(session)
    )

    step_dc_setup(session)

    if session.data["ldap_info"]:
        skip = ask_skip("[?] Found ldap data in session. Do you want to skip ldap enum step? (Y/N) ")
    elif not any(s in session.data["services"] for s in ["ldap", "ldaps"]):
        skip = ask_skip("[?] No ldap found on target? Do you want to skip ldap enum step? (Y/N) ")
    else:
        skip = ask_skip("[?] Do you want to skip ldap enum step? (Y/N)")

    run_step(
        "LDAP",
        skip,
        lambda: step_ldap_anon(session)
    )

    
    if "smb" not in session.data["services"]:
        skip = ask_skip("[?] No smb found on target? Do you want to skip smb enum step? (Y/N) ")
    else:
        skip = ask_skip("[?] Do you want to skip smb enum step? (Y/N)")

    run_step(
        "SMB",
        skip,
        lambda: step_smb(session)
    )

    run_step("RPC", False, lambda: step_rpc(session))

    if "kerberos" not in session.data["services"]:
        skip = ask_skip("[?] No kerberos found on target? Do you want to skip kerbrute and kerberoasting step? (Y/N) ")
    else:
        skip = ask_skip("[?] Do you want to skip kerbrute and kerberoasting step? (Y/N) ")

    run_step(
        "KERBRUTE",
        skip,
        lambda: step_kerbrute(session)
    )

    run_step(
        "KERBEROAST",
        skip,
        lambda: step_kerberoast(session)
    )

    if not any(s in session.data["services"] for s in ["http", "https"]):
        skip = ask_skip("[?] No http found on target? Do you want to skip web enum step? (Y/N) ")
    else:
        skip = ask_skip("[?] Do you want to skip web enum step? (Y/N) ")

    run_step(
        "WEB",
        skip,
        lambda: step_web(session)
    )


def credentialed(session):
    if not ensure_target(session):
        return

    if not session.username or not session.password:
        print(Fore.RED + "[-] Missing credentials" + Style.RESET_ALL)
        return

    if session.username not in session.data["users"]:
        session.data["users"].append(session.username)

    if (session.username, session.password) not in session.data["creds"]:
        session.data["creds"].append((session.username, session.password))

    skip = False

    if session.data["nmap_output"]:
        skip = ask_skip("[?] Found nmap data in session. Do you want to skip this step? (Y/N) ")
    else:
        skip = ask_skip("[?] Nmap may take some time depending on scan type. Do you want to skip this step (no services will be discovered)? (Y/N) ")

    run_step(
        "NMAP",
        skip,
        lambda: step_nmap(session)
    )

    step_dc_setup(session)

    run_step(
        "SERVICE ACCESS",
        False,
        lambda: session.data.update({
            "services_with_access": nxc.test_access(
                session.target,
                session.data.get("ports", []),
                session.username,
                session.password
            )
        })
    )

    if not any(s in session.data["services"] for s in ["ldap", "ldaps"]):
        skip = ask_skip("[?] No ldap found on target? Do you want to skip bloodhound enum step? (Y/N) ")
    else:
        skip = ask_skip("[?] Do you want to skip bloodhound enum step? (Y/N)")

    run_step(
        "BLOODHOUND",
        skip,
        lambda: step_bloodhound(session)
    )
