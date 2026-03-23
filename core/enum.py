#!/usr/bin/env python3
from tools import nmap, nxc, rpc, kerbrute_enum, kerberoast


def non_credentialed(session):

    if not session.target:
        print("[-] No target set")
        return

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


        save = input("[?] Save results? (y/N): ").lower() == "y"

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

        session.data["nmap_output"] = output
        print("\n[+] Scan stored in session")
        


    skip = ""
    if session.data["nmap_kerberos_output"] != "":
        skip = input("[?] Found existent nmap output related data in session. Do you want to skip this step? (Y/N) ").lower()

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
                


    print("===========================")
    print("       SMB SCANNING        ")
    print("===========================")

    skip = ""
    if session.data["smb_null_session"] == True:
        skip = input("[?] Found existent smb null session related data in session. Do you want to skip this step? (Y/N) ") .lower()

    if skip != "y":
        print("[+] Checking for smb null sessions with nxc...")
        null_session = nxc.check_null_session(session.target)
        if null_session:
            session.data["smb_null_session"] = True
            print("[+] Anonymous access to smb granted")
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


    

    print("===========================")
    print("     RPCCLIENT TESTING     ")
    print("===========================")

    print("[+] Testing commands with rpcclient null_session")
    output = rpc.anon_session(session.target)
    if output == False:
        print("[-] Could not execute commands with anonymous credentials")


    print("===========================")
    print("          KERBRUTE         ")
    print("===========================")    
    skip = ""
    if session.data["users"]:
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

    skip = input("[?] Do you want to skip ASREP-Roasting and Kerberoasting unauthenticated? (Y/N) ")
    if skip != "y":
        wordlist = input("Provide a wordlist (default=/usr/share/seclists/Usernames/top-usernames-shortlist.txt): ").strip()
        if wordlist == "":
            wordlist = "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
        print("[+] Trying Impacket GetNPUsers...")
        result = kerberoast.unauthenticated_asrep(session.target, session.domain, wordlist)

        print("[+] Trying Impacket GetUserSPNs...")
        result = kerberoast.unauthenticated_kerberoast(session.target, session.domain)







def credentialed(session):
    pass