import subprocess

def anon_session(target):
	cmd = f"rpcclient -U \"\" -N pirate.htb -c \"enumdomusers;enumdomgroups;queryuser 500;srvinfo\""

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

	keywords = [
		"NT_STATUS_ACCESS_DENIED"
	]

	for k in keywords:
		if k in output:
			return False

	return output