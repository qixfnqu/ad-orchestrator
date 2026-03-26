import subprocess
from core import aux


def anon_session(target):

    cmd = [
        "rpcclient",
        "-U", "",
        "-N",
        target,
        "-c", "enumdomusers;enumdomgroups;queryuser 500;srvinfo"
    ]

    output = aux.run_command(cmd)

    if "NT_STATUS_ACCESS_DENIED" in output:
        return False

    return output