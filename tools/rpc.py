import subprocess

def anon_session(target):

    cmd = [
        "rpcclient",
        "-U", "",
        "-N",
        target,
        "-c", "enumdomusers;enumdomgroups;queryuser 500;srvinfo"
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

    process.wait()

    if "NT_STATUS_ACCESS_DENIED" in output:
        return False

    return output