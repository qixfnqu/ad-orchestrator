#!/usr/bin/env python3
from tools import nmap, nxc, rpc, kerbrute_enum, kerberoast, web_enum, ldap, smbclient
from core import config_manager

from core.aux import get_services, has_any_service
import re

import time

from colorama import init, Fore, Back, Style



def is_probable_dc(ports):
    services = get_services(ports)

    required = {"kerberos", "ldap"}
    optional = {"smb", "rpc", "dns"}

    if not required.issubset(services):
        return False

    score = sum(1 for s in optional if s in services)
    return score >= 1

def extract_domain(nmap_output):
    match = re.search(r"Domain:\s*([a-zA-Z0-9\.\-]+)", nmap_output)
    if match:
        return match.group(1).lower()

    match = re.search(r"Nmap scan report for .*?\.(\S+)", nmap_output)
    if match:
        return match.group(1).split(".")[1] + "." + match.group(1).split(".")[2].lower()

    return None


def non_credentialed(session):

    if not session.target:
        print(Fore.RED + "[-] No target set" + Style.RESET_ALL)
        return

    if session.target not in session.data["hosts"]:
        session.data["hosts"].append(session.target)



    ## 1. NMAP SCANNING    

    print("\n")
    print(Fore.CYAN + "[      NMAP SCANNING      ]" + Style.RESET_ALL)
    print("\n")

    skip = ""
    nmap_output = ""
    if session.data["nmap_output"] != "":
        skip = input("[?] Found existent nmap output related data in session. Do you want to skip this step? (Y/N) ").lower()
    else:
        skip = input("[?] Depending on the scan type, this may take some time. Do you want to skip this step? (Y/N) ").lower()

    if skip != "y":
        #Step 1
        print("Choose nmap scan type:")
        print("    1) Basic")
        print("    2) Extensive")

        mode = input("> ").strip()


        save = input("[?] Save results to a file? (Y/N): ").lower() == "y"

        print("\n[+] Ready to run scan")
        print(f"\tTarget: {session.target}")
        print(f"\tMode: {'Extensive' if mode == '2' else 'Basic'}")

        confirm = input("\n[?] Execute? (Y/N): ").lower()
        if confirm not in ["", "y"]:
            print("[*] Aborted")
            return

        print("[+] Running nmap scan...")
        if mode == "2":
            nmap_output = nmap.extensive_scan(session.target, save)
        else:
            nmap_output = nmap.basic_scan(session.target, save)

        session.data["nmap_output"] = nmap_output[0]
        session.data["ports"] = nmap_output[1]
        print("\n[+] Scan stored in session")

        services = get_services(session.data["ports"])
        session.data["services"] = services

    if is_probable_dc(session.data["ports"]) and not session.dc_config:
        print("[+] Target looks like a Domain Controller")

        choice = input("[?] Configure DC settings (krb5.conf, /etc/hosts)? (Y/N): ").lower()

        if choice == "y":
            dc_ip = session.target
            if session.domain:
                domain = session.domain.lower()
            else:
                domain = extract_domain(nmap_output[0]).lower()
                if domain == None:
                    print(Fore.RED + "[-] Couldn't automatically extract domain." + Style.RESET_ALL)
                else:
                    session.domain = domain.lower()
    
                    config_manager.generate_krb5(domain, dc_ip)
                    session.dc_config = True

                    add_host = input("[?] Add a new /etc/hosts entry? (Y/N) ").lower()
                    if add_host == "y":
                        config_manager.generate_etc_hosts(dc_ip, domain, True)
        
    skip = ""

    if "kerberos" not in session.data["services"]:
        skip = input("[?] Nmap didn't detect kerberos running on the system, do you want to skip kerberos nmap scan? (Y/N) ").lower()
    elif session.data["nmap_kerberos_output"] != "":
        skip = input("[?] Found existent nmap kerberos scan data in session. Do you want to skip this step? (Y/N) ").lower()

    if skip != "y":
        
        k_choice = input("[?] Do you want to perform kerberos-related script scan on the target? (Y/N) ").lower()
        if k_choice == "y":    
            if not session.domain:
                print(Fore.RED + "[-] No domain/realm set for the kerberos scan" + Style.RESET_ALL)
            else:
                print("Choose a username wordlist path (Default: /usr/share/wordlists/common-usernames.txt")
                dict_path = input("> ").strip()
                if dict_path == "":
                    dict_path = "/usr/share/wordlists/common-usernames.txt"
                print(f"Username dictionary: {dict_path}")
                save = input("[?] Save results? (Y/N): ").lower() == "y"
                output = nmap.kerberos_scan(session.target, session.domain.upper(), dict_path, save)
                session.data["nmap_kerberos_output"] = output
                
    ## 2. LDAP SCANNING 

    time.sleep(0.5)
    print("\n")
    print(Fore.CYAN + "[     LDAP ENUMERATION    ]" + Style.RESET_ALL)
    print("\n")


    skip = ""
    if not any(s in session.data["services"] for s in ["ldap", "ldaps", "globalcatLDAP", "globalcatLDAPssl"]):
        skip = input("[?] Nmap didn't detect LDAP open on the system, do you want to skip ldap scan? (Y/N) ").lower()
    elif session.data["ldap_info"] != "":
        skip = input("[?] Found existent ldap related data in session. Do you want to skip this step? (Y/N) ") .lower()

    if skip != "y":
        print("[+] Trying to recover information with ldapsearch...")
        output = ldap.anon_bind(session.target, [389, 636, 3268, 3269])

        print(Fore.GREEN + "[+] Saving data to session" + Style.RESET_ALL)
        session.data["ldap_info"] = output


    ## 3. SMB SCANNING 

    time.sleep(0.5)
    print("\n")
    print(Fore.CYAN + "[      SMB SCANNING       ]" + Style.RESET_ALL)
    print("\n")

    skip = ""

    if "smb" not in session.data["services"]:
        skip = input("[?] Nmap didn't detect SMB open on the system, do you want to skip smb scan? (Y/N) ").lower()
    elif session.data["smb_null_session"] == True:
        skip = input("[?] Found existent smb null session related data in session. Do you want to skip this step? (Y/N) ") .lower()

    if skip != "y":
        print("[+] Checking for smb null sessions with nxc...")
        null_session = nxc.check_null_session(session.target)
        if null_session:
            session.data["smb_null_session"] = True
            print(Fore.GREEN + "[+] Anonymous access to smb found" + Style.RESET_ALL)

            skip = ""
            if session.data["smb_shares"]:
                skip = input("[?] Found existent smb shares listed in session. Do you want to skip this step? (Y/N) ") .lower()
            if skip != "y":
                print("[+] Listing shares, password policy, users, and RIDs with anonymous credentials")
                output = nxc.smb_enum(session.target)
                if output == False:
                    print(Fore.RED + "[-] Could not enumerate shares with nxc, trying smbclient..." + Style.RESET_ALL)
                    session.data["smb_shares"] = smbclient.list_shares(session.target)
                else:
                    session.data["smb_null_session"] = False
                    print(Fore.RED + "[-] No anonymous smb access on target" + Style.RESET_ALL)


    ## 4. RPCCLIENT SCANNING
    
    time.sleep(0.5)
    print("\n")
    print(Fore.CYAN + "[    RPCCLIENT TESTING    ]" + Style.RESET_ALL)
    print("\n")

    print("[+] Testing commands with rpcclient null_session")
    output = rpc.anon_session(session.target)
    if output == False:
        print(Fore.RED + "[-] Could not execute commands with anonymous credentials" + Style.RESET_ALL)


    ## 5. KERBEROS RELATED SCANNING

    time.sleep(0.5)
    print("\n")
    print(Fore.CYAN + "[        KERBRUTE         ]" + Style.RESET_ALL)
    print("\n")   
    skip = ""

    if "kerberos" not in session.data["services"]:
        skip = input("[?] Nmap didn't detect kerberos running on the system, do you want to skip kerbrute phase? (Y/N) ").lower()
    elif session.data["users"]:
        skip = input("[?] Found existent usernames in session. Do you want to skip this step? (Y/N) ") .lower()
    else:
        skip = input("[?] Do you want to skip kerbrute enumeration? (Y/N) ").lower()

    if skip != "y":
        if not session.domain:
            print(Fore.RED + "[-] No domain/realm set for kerbrute enumeration" + Style.RESET_ALL)
        else:
            wordlist = input("Provide a wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip()
            if wordlist == "":
                wordlist = "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
            result = kerbrute_enum.user_enum(session.domain, session.target, wordlist)

            if len(result["users"]) != 0:
                print(Fore.GREEN + "[+] Saved found users into session" + Style.RESET_ALL)
                session.data["users"] = list(set(session.data["users"] + result["users"]))


    time.sleep(0.5)
    print("\n")
    print(Fore.CYAN + "[      KERBEROASTING      ]" + Style.RESET_ALL)
    print("\n")
    skip = ""

    if "kerberos" not in session.data["services"]:
        skip = input("[?] Nmap didn't detect kerberos running on the system, do you want to skip kerberoasting phase? (Y/N) ").lower()
    else:    
        skip = input("[?] Do you want to skip ASREP-Roasting and Kerberoasting unauthenticated? (Y/N) ").lower()

    if skip != "y":
        if not session.domain:
            print(Fore.RED + "[-] No domain/realm set for kerbrute enumeration" + Style.RESET_ALL)
        else:    
            wordlist = input("Provide a wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip()
            if wordlist == "":
                wordlist = "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
            print("[+] Trying Impacket GetNPUsers...")
            result = kerberoast.unauthenticated_asrep(session.target, session.domain, wordlist)

            print("[+] Trying Impacket GetUserSPNs...")
            result = kerberoast.unauthenticated_kerberoast(session.target, session.domain)


    ## 6. BASIC WEB ENUM

    time.sleep(0.5)
    print("\n")
    print(Fore.CYAN + "[      WEB ENUMERATION     ]" + Style.RESET_ALL)
    print("\n")
    skip = ""

    if not any(s in session.data["services"] for s in ["http", "https"]):
        skip = input("[?] Nmap didn't detect open web running on the system, do you want to skip web enumeration? (Y/N) ").lower()
    else:
        skip = input("[?] Do you want to skip web enumeration? (Y/N) ").lower() 

    if skip != "y":
        add_host = input("[?] Do you want to add the ip entry to /etc/hosts? (Y/N) ").lower()
        if add_host == "y":
            if session.domain:
                print("[+] Generating /etc/hosts with provided domain")
            else:
                domain = input("Enter the domain name: ").strip().lower()
                session.domain = domain

            config_manager.generate_etc_hosts(session.target, session.domain)

        scan_target = ""
        if session.domain:
            scan_target = session.domain
        else:
            scan_target = session.target

        use_https = "https" in session.data["services"]

        web_enum.basic_web_enum(scan_target, use_https)

        fuzzing = input("[?] Do you want to perform fuzzing with Gobuster? (Y/N) ").lower()
        if fuzzing == 'y':
            wordlist = input("Provide a wordlist (default=/usr/share/wordlists/dirb/common.txt): ").strip()
            if wordlist == "":
                wordlist = "/usr/share/wordlists/dirb/common.txt"
            routes = web_enum.fuzz(scan_target, use_https, wordlist)
            if len(routes) != 0:
                session.data["routes"] = list(set(session.data["routes"] + routes))

        web_scan = input("[?] Do you want to perform an additional web-related nmap scan? (Y/N) ").lower()
        if web_scan == 'y':
            print("[+] Running another nmap scan...")
            nmap.web_scan(scan_target)

        subdomain_discovery = input("[?] Do you want to perform subdomain discovery? (Y/N) ").lower()
        if subdomain_discovery == 'y':
            mode = input("[?] Choose mode (normal/vhost, default: normal): ").lower()
            if mode != "normal" and mode != "vhost":
                mode = "normal"
            wordlist = input("Provide a wordlist (default=/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt): ").strip()
            if wordlist == "":
                wordlist = "/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt"
            subdomains = web_enum.subdomain_discovery(session.target, scan_target, mode, wordlist, use_https)
            session.data["subdomains"] = list(set(session.data["subdomains"] + subdomains))


            if len(subdomains) != 0 and mode == "vhost":
                add_vhost = input("[+] Found valid vhosts, do you want to add /etc/hosts entries? (Y/N) ").lower()
                if add_vhost == "y":
                    config_manager.add_vhost(session.target, session.domain, subdomains)


def credentialed(session):
    if not session.target:
        print(Fore.RED + "[-] No target set" + Style.RESET_ALL)
        return

    if session.target not in session.data["hosts"]:
        session.data["hosts"].append(session.target)

    if not session.username or not session.password:
        print(Fore.RED + "[-] No username/password set" + Style.RESET_ALL)
        return

    if len(session.data["users"]) == 0:
        session.data["users"].append(session.username)

    if len(session.data["creds"]) == 0:
        session.data["creds"].append((session.username, session.password))

    ## 1. NMAP SCANNING

    print("\n")
    print(Fore.CYAN + "[      NMAP SCANNING      ]" + Style.RESET_ALL)
    print("\n")

    skip = ""
    nmap_output = ""
    if session.data["nmap_output"] != "":
        skip = input("[?] Found existent nmap output related data in session. Do you want to skip this step? (Y/N) ").lower()
    else:
        skip = input("[?] Depending on the scan type, this may take some time. Do you want to skip this step? (Y/N) ").lower()

    if skip != "y":
        #Step 1
        print("Choose nmap scan type:")
        print("    1) Basic")
        print("    2) Extensive")

        mode = input("> ").strip()


        save = input("[?] Save results to a file? (Y/N): ").lower() == "y"

        print("\n[+] Ready to run scan")
        print(f"\tTarget: {session.target}")
        print(f"\tMode: {'Extensive' if mode == '2' else 'Basic'}")

        confirm = input("\n[?] Execute? (Y/N): ").lower()
        if confirm not in ["", "y"]:
            print("[*] Aborted")
            return

        print("[+] Running nmap scan...")
        if mode == "2":
            nmap_output = nmap.extensive_scan(session.target, save)
        else:
            nmap_output = nmap.basic_scan(session.target, save)

        session.data["nmap_output"] = nmap_output[0]
        session.data["ports"] = nmap_output[1]
        print("\n[+] Scan stored in session")

        services = get_services(session.data["ports"])
        session.data["services"] = services

    if is_probable_dc(session.data["ports"]) and not session.dc_config:
        print("[+] Target looks like a Domain Controller")

        choice = input("[?] Configure DC settings (krb5.conf, /etc/hosts)? (Y/N): ").lower()

        if choice == "y":
            dc_ip = session.target
            if session.domain:
                domain = session.domain.lower()
            else:
                domain = extract_domain(nmap_output[0]).lower()
                if domain == None:
                    print(Fore.RED + "[-] Couldn't automatically extract domain." + Style.RESET_ALL)
                else:
                    session.domain = domain.lower()
    
                    config_manager.generate_krb5(domain, dc_ip)
                    session.dc_config = True

                    add_host = input("[?] Add a new /etc/hosts entry? (Y/N) ").lower()
                    if add_host == "y":
                        config_manager.generate_etc_hosts(dc_ip, domain, True)
        

    print("\n")
    print(Fore.CYAN + "[      TRYING SERVICES      ]" + Style.RESET_ALL)
    print("\n")    
    skip = ""

    if len(session.data["services_with_access"]) != 0:
        skip = input("[?] Found services with access in session data, do you want to skip this part? (Y/N) ").lower()
    
    if skip != 'y':
        result = nxc.test_access(session.target, session.data["ports"], session.username, session.password)
        if len(result) != 0:
            session.data["services_with_access"] = result