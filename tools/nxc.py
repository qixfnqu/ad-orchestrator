import subprocess


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