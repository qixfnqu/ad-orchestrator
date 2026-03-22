import subprocess
import re


def user_enum(domain, dc_ip, wordlist):
    cmd = f"kerbrute -users {wordlist} -domain {domain} -dc-ip {dc_ip}"

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output = ""

    for line in process.stdout:
        print(line, end="")
        output += line

    process.wait()

 
    users = []

    for line in output.splitlines():
        if "Valid user" in line:
            match = re.search(r"Valid user\s*=>\s*(\S+)", line)
            if match:
                users.append(match.group(1))


    return {
        "users": users,
        "output": output
    }