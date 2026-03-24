import subprocess
import re


def user_enum(domain, dc_ip, wordlist):
    cmd = f"kerbrute userenum  -d {domain} --dc {dc_ip} {wordlist}"

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
        if "valid username" in line.lower():
            match = re.search(r"\[\+\]\s*VALID USERNAME:\s*(\S+)", line, re.IGNORECASE)
            if match:
                users.append(match.group(1).split("@")[0])


    return {
        "users": users,
        "output": output
    }