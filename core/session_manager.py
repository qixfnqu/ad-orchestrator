import json
from colorama import Fore, Back, Style

class Session:
    def __init__(self):
        self.target = None
        self.domain = None
        self.username = None
        self.password = None
        self.dc_config = False
        self.data = {
            "users": [],
            "hashes": [],
            "hosts": [],
            "computers": [],
            "creds": [],
            "ports": [],
            "services": [],
            "nmap_output": "",
            "smb_null_session": False,
            "smb_shares": [],
            "ldap_info": "",
            "routes": [],
            "subdomains": [],
            "services_with_access": []
        }

    def to_dict(self):
        return {
            "target": self.target,
            "domain": self.domain,
            "username": self.username,
            "password": self.password,
            "dc_config": self.dc_config,
            "data": self.data
        }

    def from_dict(self, d):
        required_fields = ["target", "domain", "username", "password", "dc_config", "data"]
        for field in required_fields:
            if field not in d:
                print(Fore.RED + f"[-] Session data is corrupted or missing field: {field}" + Style.RESET_ALL)
                return {"error": True}

        if not isinstance(d["data"], dict):
            print(Fore.RED + "[-] Session data is corrupted: 'data' should be a dictionary" +  Style.RESET_ALL)
            return {"error": True}

        self.target = d.get("target")
        self.domain = d.get("domain")
        self.username = d.get("username")
        self.password = d.get("password")
        self.dc_config = d.get("dc_config", False)
        self.data = d.get("data", self.data)

        return {"error": False}