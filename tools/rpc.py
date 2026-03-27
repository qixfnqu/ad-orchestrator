from impacket.dcerpc.v5 import transport, samr
from impacket.dcerpc.v5.rpcrt import DCERPCException
from colorama import Fore, Style

def anon_session(target):
    print(f"[*] Trying anonymous RPC enumeration on {target}...")
    

    string_binding = f'ncacn_np:{target}[\\pipe\\samr]'
    rpctransport = transport.DCERPCTransportFactory(string_binding)
    rpctransport.set_credentials('', '') 
    
    try:
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(samr.MSRPC_UUID_SAMR)
        
        handle = samr.hSamrConnect(dce)['getHandle']
        
        domains = samr.hSamrEnumerateDomainsInSamServer(dce, handle)
        domain_name = domains['Buffer']['Element'][0]['Name']
        print(Fore.GREEN + f"[+] Found domain: {domain_name}" + Style.RESET_ALL)
        
        sid = samr.hSamrLookupDomainInSamServer(dce, handle, domain_name)['DomainId']
        
        domain_handle = samr.hSamrOpenDomain(dce, handle, sid)['getHandle']
        
        users = samr.hSamrEnumerateUsersInDomain(dce, domain_handle)['Buffer']['Element']
        user_list = [u['Name'] for u in users]
        
        print(Fore.GREEN + f"[+] Found {len(user_list)} users" + Style.RESET_ALL)
        
        samr.hSamrCloseHandle(dce, domain_handle)
        dce.disconnect()
        
        return {
            "domain": domain_name,
            "users": user_list,
            "success": True
        }

    except DCERPCException as e:
        if "STATUS_ACCESS_DENIED" in str(e):
            print(Fore.RED + "[-] No anonymous session." + Style.RESET_ALL)
        else:
            print(f"[-] Error RPC: {e}")
        return False
