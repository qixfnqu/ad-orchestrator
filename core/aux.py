import re
from core.config import PORT_SERVICE_MAP

from subprocess import Popen, PIPE, STDOUT


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def normalize_service(service):
    if service.startswith("http"):
        return "http"
    if service.startswith("https"):
        return "https"
    return service

def get_service(port):
    return normalize_service(PORT_SERVICE_MAP.get(port, "unknown"))

def get_services(ports):
    return list(set(get_service(p) for p in ports))


def has_service(ports, service):
    return service in get_services(ports)

def has_any_service(ports, services):
    detected = get_services(ports)
    return any(s in detected for s in services)

def is_valid_target(value):
    ip = re.match(r"^\d{1,3}(\.\d{1,3}){3}$", value)
    hostname = re.match(r"^[a-zA-Z0-9\-\.]+$", value)
    return bool(ip or hostname)

def run_command(cmd, cwd=None) -> str:
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT, text=True, cwd=cwd)
    output = ""
    for line in process.stdout:
        print(line, end="")
        output += line
    process.wait()
    return output
