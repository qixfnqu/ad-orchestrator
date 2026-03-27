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
