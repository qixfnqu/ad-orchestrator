import subprocess
import re

from core import aux
import xml.etree.ElementTree as ET

import os

def parse_ports(xml_file):
    ports = []

    xml_content = ""
    if os.path.exists(xml_file):
        with open(xml_file, "r") as f:
            xml_content = f.read()

    try:
        root = ET.fromstring(xml_content)
        
        for port_element in root.findall(".//port"):
            state = port_element.find("state").get("state")
            if state == "open":
                port_id = int(port_element.get("portid"))
                
                ports.append(port_id)
        
    except ET.ParseError:
        print("[-] Error parseando el XML de Nmap")
        
    return ports



def run_scan(target, cmd):
    output = aux.run_command(cmd)
    ports = parse_ports(f"{target}_scan.xml")

    return [output, ports]


def basic_scan(target):
    cmd = ["nmap", "-sC", "-sV", target, "-oX", f"{target}_scan.xml"]


    return run_scan(target, cmd)


def extensive_scan(target, save=False):
    cmd = [
        "nmap",
        "-sUV",
        "-sC",
        "-p", "53,88,123,135,137,139,389,445,464,636,3268,3269",
        "--script=banner,ldap*,smb*,krb5*,msrpc*",
        "--script-args", "ldap.show-all-info=true,unsafe=1",
        target
    ]
    cmd += ["-oX", f"{target}_scan.xml"]

    return run_scan(target, cmd)

def kerberos_scan(target, realm, dict_path, save=False):
    cmd = [
        "nmap",
        "-p", "88",
        "--script", "krb5-enum-users",
        "--script-args",
        f"krb5-enum-users.realm={realm},krb5-enum-users.userdict={dict_path}",
        target
    ]
    
    cmd += ["-oX", f"{target}_kerberos_scan.xml"]

    return run_scan(target, cmd)

def web_scan(target):
    cmd = [
        "nmap",
        "-sV",
        "-sC",
        "--script", "http-enum,http-wordpress*,http-drupal*,http-php-version,http-vuln*",
        "-p", "80,443,8080,8443",
        "--script-args", "http.useragent=Mozilla/5.0",
        target
    ]


    return run_scan(target, cmd)
