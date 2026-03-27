<<<<<<< HEAD
import subprocess
from colorama import Fore, Back, Style
from core import aux


def parse_smb_shares(output):
    shares = []
    parsing = False

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("Sharename"):
            parsing = True
            continue

        if parsing and line.startswith("----"):
            continue
        
        if parsing and line == "":
            break

        if parsing:
            parts = line.split()
  
            if len(parts) >= 2:
                share = parts[0]
                share_type = parts[1]

                
                if share_type in ["Disk", "IPC", "Printer"]:
                    shares.append(share)

    print(Fore.GREEN + f"[+] Found {len(shares)} shares")
    return shares



def list_shares(target, username="", password=""):
    if username == "" or password == "":
        cmd = ["smbclient", "-L", f"\\\\{target}\\", "-N"]
    else:
        cmd = ["smbclient", "-L", f"\\\\{target}\\", "-U", f"{username}%{password}"]

    output = aux.run_command(cmd)

    shares = parse_smb_shares(output)
    return shares
=======
from impacket.smbconnection import SMBConnection
from colorama import Fore, Style

def list_shares(target, username="", password="", domain=""):
    shares = []
    try:
        conn = SMBConnection(target, target, sess_port=445)
        
        if username == "" or password == "":
            conn.login('', '')
        else:
            conn.login(username, password, domain)

        smb_shares = conn.listShares()
        
        for share in smb_shares:
            share_name = share['shi1_netname'][:-1]
            print(Fore.GREEN + "[+] Found share: {share_name}" + Style.RESET_ALL)
            shares.append(share_name)

        print(Fore.GREEN + f"[+] Found {len(shares)} shares" + Style.RESET_ALL)
        
        conn.logoff()
        return shares

    except Exception as e:
        if "STATUS_ACCESS_DENIED" in str(e):
            print(Fore.RED + "[-] SMB Access Denied (Null Session likely disabled)" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"[-] SMB Error: {e}" + Style.RESET_ALL)
        return []
>>>>>>> 49bd065 (Refactor some functionality to native impacket library)
