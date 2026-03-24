import subprocess
from core.config import NXC_SERVICE_MAP
from colorama import Fore, Back, Style


def check_null_session(target):
    cmd = ["nxc", "smb", target, "-u", "", "-p", ""]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    output = result.stdout

    keywords = [
        "Pwn3d",
        "STATUS_SUCCESS",
        "Null Auth:True",
        "Guest session"
    ]

    for k in keywords:
        if k in output:
            return True

    return False


def anonymous_enum(target):
    cmd = f'nxc smb {target} -u "" -p "" --shares --users --pass-pol --rid-brute'

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

    keywords = [
        "STATUS_ACCESS_DENIED",
        "Error enumerating shares"
    ]

    for k in keywords:
        if k in output:
            return False

    return output


def get_nxc_modules(ports):
    modules = set()

    for p in ports:
        if p in NXC_SERVICE_MAP:
            modules.add(NXC_SERVICE_MAP[p])

    return list(modules)

def test_access(target, ports, username="", password=""):
    services_with_access = []
    modules = get_nxc_modules(ports)

    for module in modules:
        cmd = f'nxc {module} {target} -u \'{username}\' -p \'{password}\''

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

        keywords = [
        "Pwn3d",
        "STATUS_SUCCESS",
        "[+]"
        ]

        for k in keywords:
            if k in output:
                services_with_access.append(module)
                print(Fore.GREEN + Style.BRIGHT + f"[+] User {username} has access to {module} with password {password}" + Style.RESET_ALL)

        cmd = f'nxc {module} {target} -u \'{username}\' -p \'{password}\' --local-auth'

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

        keywords = [
        "Pwn3d",
        "STATUS_SUCCESS",
        "[+]"
        ]

        for k in keywords:
            if k in output:
                services_with_access.append(module)
                print(Fore.GREEN + f"[+] User {username} has access to {module}" + Style.RESET_ALL)

    return services_with_access
