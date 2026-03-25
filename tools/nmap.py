import subprocess

import re

def parse_ports(output):
    ports = []

    for line in output.splitlines():
        match = re.match(r"(\d+)\/\w+\s+open", line)
        
        if match:
            port = int(match.group(1))
            ports.append(port)

    return ports

def run_scan(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output = ""

    for line in process.stdout:
        print(line, end="")
        output += line

    process.wait()

    ports = parse_ports(output)

    return [output, ports]


def basic_scan(target, save=False):
    cmd = ["nmap", "-sC", "-sV", target]

    if save:
        cmd += ["-oN", f"{target}_scan.txt"]

    return run_scan(cmd)


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

    if save:
        cmd += ["-oN", f"{target}_scan.txt"]

    return run_scan(cmd)

def kerberos_scan(target, realm, dict_path, save=False):
    cmd = [
        "nmap",
        "-p", "88",
        "--script", "krb5-enum-users",
        "--script-args",
        f"krb5-enum-users.realm={realm},krb5-enum-users.userdict={dict_path}",
        target
    ]

    if save:
        cmd += ["-oN", f"{target}_kerberos_scan.txt"]

    return run_scan(cmd)

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

    return run_scan(cmd)