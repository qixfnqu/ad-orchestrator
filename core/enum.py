#!/usr/bin/env python3
from tools import nmap, nxc, rpc, kerbrute_enum, kerberoast, web_enum
from core import config_manager


def is_probable_dc(ports):
    score = 0

    if 88 in ports:   
        score += 2
    if 389 in ports:  
        score += 2
    if 445 in ports:  
        score += 1
    if 135 in ports: 
        score += 1
    if 53 in ports:   
        score += 1
    if 3268 in ports: 
        score += 2

    return score >= 4


def non_credentialed(session):

    if not session.target:
        print("[-] No target set")
        return

    session.data["hosts"].append(session.target)

    print("\n")
    print("===========================")
    print("       NMAP SCANNING       ")
    print("===========================")

    skip = ""
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


        save = input("[?] Save results to a file? (y/N): ").lower() == "y"

        print("\n[+] Ready to run scan")
        print(f"Target: {session.target}")
        print(f"Mode: {'Extensive' if mode == '2' else 'Basic'}")

        confirm = input("\n[?] Execute? (Y/n): ").lower()
        if confirm not in ["", "y"]:
            print("[*] Aborted")
            return

        print("[+] Running nmap scan...")
        if mode == "2":
            output = nmap.extensive_scan(session.target, save)
        else:
            output = nmap.basic_scan(session.target, save)

        session.data["nmap_output"] = output[0]
        session.data["ports"] = output[1]
        print("\n[+] Scan stored in session")

    if is_probable_dc(session.data["ports"]) and not session.dc_config:
        print("[+] Target looks like a Domain Controller")

        choice = input("[?] Configure DC settings (krb5.conf, /etc/hosts)? (Y/n): ").lower()

        if choice == "y":
            dc_ip = session.target
            domain = session.domain.lower()
    
            config_manager.generate_krb5(domain, dc_ip)
            session.dc_config = True
        

    skip = ""

    if 88 not in session.data["ports"]:
        skip = input("[?] Nmap didn't detect kerberos running on the system, do you want to skip kerberos nmap scan? (Y/N) ").lower()
    elif session.data["nmap_kerberos_output"] != "":
        skip = input("[?] Found existent nmap kerberos scan data in session. Do you want to skip this step? (Y/N) ").lower()

    if skip != "y":
        #Step 2
        k_choice = input("[?] Do you want to perform kerberos-related script scan on the target? (Y/N) ").lower()
        if k_choice == "y":    
            if not session.domain:
                print("[-] No domain/realm set for the kerberos scan")
            else:
                print("Choose a username wordlist path (Default: /usr/share/wordlists/common-usernames.txt")
                dict_path = input("> ").strip()
                if dict_path == "":
                    dict_path = "/usr/share/wordlists/common-usernames.txt"
                print(f"Username dictionary: {dict_path}")
                save = input("[?] Save results? (y/N): ").lower() == "y"
                output = nmap.kerberos_scan(session.target, session.domain.upper(), dict_path, save)
                session.data["nmap_kerberos_output"] = output
                

    print("\n")
    print("===========================")
    print("       SMB SCANNING        ")
    print("===========================")

    skip = ""

    if 445 not in session.data["ports"]:
        skip = input("[?] Nmap didn't detect SMB open on the system, do you want to skip smb scan? (Y/N) ").lower()
    elif session.data["smb_null_session"] == True:
        skip = input("[?] Found existent smb null session related data in session. Do you want to skip this step? (Y/N) ") .lower()

    if skip != "y":
        print("[+] Checking for smb null sessions with nxc...")
        null_session = nxc.check_null_session(session.target)
        if null_session:
            session.data["smb_null_session"] = True
            print("[+] Anonymous access to smb found")

            skip = ""
            if session.data["smb_shares"]:
                skip = input("[?] Found existent smb shares listed in session. Do you want to skip this step? (Y/N) ") .lower()
            if skip != "y":
                print("[+] Listing shares, password policy, users, and RIDs with anonymous credentials")
                output = nxc.anonymous_enum(session.target)
                if output == False:
                    print("[-] Could not enumerate shares with anonymous credentials")
                else:
                    session.data["smb_null_session"] = False
                    print("[-] No anonymous smb access on target")


    
    print("\n")
    print("===========================")
    print("     RPCCLIENT TESTING     ")
    print("===========================")

    print("[+] Testing commands with rpcclient null_session")
    output = rpc.anon_session(session.target)
    if output == False:
        print("[-] Could not execute commands with anonymous credentials")


    print("\n")
    print("===========================")
    print("          KERBRUTE         ")
    print("===========================")    
    skip = ""

    if 88 not in session.data["ports"]:
        skip = input("[?] Nmap didn't detect kerberos running on the system, do you want to skip kerbrute phase? (Y/N) ").lower()
    elif session.data["users"]:
        skip = input("[?] Found existent usernames in session. Do you want to skip this step? (Y/N) ") .lower()
    else:
        skip = input("[?] Do you want to skip kerbrute enumeration? (Y/N) ").lower()

    if skip != "y":
        if not session.domain:
            print("[-] No domain/realm set for kerbrute enumeration")
        else:
            wordlist = input("Provide a wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip()
            if wordlist == "":
                wordlist = "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
            result = kerbrute_enum.user_enum(session.domain, session.target, wordlist)
            if len(result["users"]) != 0:
                print("[+] Saved found users into session")
                session.data["users"] = result["users"]


    print("\n")
    print("===========================")
    print("       KERBEROASTING       ")
    print("===========================")
    skip = ""

    if 88 not in session.data["ports"]:
        skip = input("[?] Nmap didn't detect kerberos running on the system, do you want to skip kerbrute phase? (Y/N) ").lower()
    else:    
        skip = input("[?] Do you want to skip ASREP-Roasting and Kerberoasting unauthenticated? (Y/N) ").lower()

    if skip != "y":
        wordlist = input("Provide a wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip()
        if wordlist == "":
            wordlist = "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
        print("[+] Trying Impacket GetNPUsers...")
        result = kerberoast.unauthenticated_asrep(session.target, session.domain, wordlist)

        print("[+] Trying Impacket GetUserSPNs...")
        result = kerberoast.unauthenticated_kerberoast(session.target, session.domain)

    print("\n")
    print("===========================")
    print("      WEB ENUMERATION      ")
    print("===========================")
    skip = ""

    if 80 not in session.data["ports"] and 443 not in session.data["ports"]:
        skip = input("[?] Nmap didn't detect open web running on the system, do you want to skip web enumeration? (Y/N) ").lower()
    else:
        skip = input("[?] Do you want to skip web enumeration? (Y/N) ").lower() 

    if skip != "y":
        add_host = input("[?] Do you want to add the ip entry to /etc/hosts? (Y/N) ").lower()
        if add_host == "y":
            domain = input("Enter the domain name: ").strip().lower()
            session.domain = domain
            config_manager.generate_etc_hosts(session.target, domain)

        scan_target = ""
        if session.domain:
            scan_target = session.domain
        else:
            scan_target = session.target

        use_https = 443 in session.data["ports"]
        web_enum.basic_web_enum(scan_target, use_https)

        fuzzing = input("[?] Do you want to perform fuzzing with Gobuster? (Y/N) ").lower()
        if fuzzing == 'y':
            wordlist = input("Provide a wordlist (default=/usr/share/wordlists/dirb/common.txt): ").strip()
            if wordlist == "":
                wordlist = "/usr/share/wordlists/dirb/common.txt"
            web_enum.fuzz(scan_target, use_https, wordlist)

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
            session.data["subdomains"] = subdomains

            if len(subdomains) != 0 and mode == "vhost":
                add_vhost = input("[+] Found valid vhosts, do you want to add /etc/hosts entries? (Y/N) ").lower()
                if add_vhost == "y":
                    config_manager.add_vhost(session.target, session.domain, subdomains)

def credentialed(session):
    pass