import logging
from impacket.krb5 import kerberosv5
from impacket.krb5 import constants
from colorama import Fore, Style

logging.getLogger("impacket").setLevel(logging.ERROR)

def user_enum(domain, dc_ip, wordlist_path):
    valid_users = []
    domain = domain.upper()
    
    try:
        with open(wordlist_path, 'r') as f:
            usernames = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}{Style.RESET_ALL}")
        return {"users": []}

    for user in usernames:
        try:
            kerberosv5.getKerberosASREP(
                user, 
                domain, 
                None, 
                dc_ip, 
                dc_ip
            )
            print(f"{Fore.GREEN}[+] VALID USER (No Pre-auth): {user}{Style.RESET_ALL}")
            valid_users.append(user)

        except Exception as e:
            error_code = getattr(e, 'error_code', None)
            
            if error_code == constants.ErrorCodes.KDC_ERR_PREAUTH_REQUIRED.value:
                print(f"{Fore.GREEN}[+] VALID USER: {user}{Style.RESET_ALL}")
                valid_users.append(user)
            elif error_code == 24:
                print(f"{Fore.YELLOW}[!] VALID USER (Locked/Disabled): {user}{Style.RESET_ALL}")
                valid_users.append(user)
            else:
                continue

    return {
        "users": valid_users,
        "count": len(valid_users)
    }