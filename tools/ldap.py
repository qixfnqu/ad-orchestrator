import subprocess
from core.config import NXC_SERVICE_MAP

def anon_bind(target, ports):
	idx = 0 
	output = ""

	while True:
		print(f"[+] Trying on port {ports[idx]}")

		cmd = f"ldapsearch -x -H ldap://{target}:{ports[idx]} -s base \"(objectclass=*)\""

		process = subprocess.Popen(
			cmd,
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True
		)

		for line in process.stdout:
			print(line, end="")
			output += line

		idx += 1

		if output != "ldap_result: Can't contact LDAP server (-1)":	
			break

	return output