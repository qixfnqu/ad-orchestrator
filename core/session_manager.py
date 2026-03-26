import json

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
            "creds": [],
            "ports": [],
            "services": [],
            "nmap_output": "",
            "nmap_kerberos_output": "",
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
        self.target = d.get("target")
        self.domain = d.get("domain")
        self.username = d.get("username")
        self.password = d.get("password")
        self.dc_config = d.get("dc_config", False)
        self.data = d.get("data", self.data)