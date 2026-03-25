import subprocess
import os

from colorama import Fore, Back, Style


def bh_enum(target, domain, username, password):
	output_dir = input("[?] Choose output dir for the jsons (default=/tmp/bh_output): ").strip()
	if output_dir == "":
		output_dir = "/tmp/bh_output"

	os.makedirs(output_dir, exist_ok=True)

	cmd = [
		"bloodhound-python",
		"-d", domain,
		"-dc", domain,
		"-ns", target,
		"-u", username,
		"-p", password,
		"-c", "All"
	]

	try:
		process = subprocess.Popen(
	        cmd,
	        stdout=subprocess.PIPE,
	        stderr=subprocess.STDOUT,
	        text=True,
	        cwd=output_dir 
	    )

		output = ""

		for line in process.stdout:
			print(line, end="")
			output += line
		process.wait()

	except Exception as e:
		print(Fore.RED + f"[-] BloodHound scan failed with: {e}" + Style.RESET_ALL)
		return

	print(Fore.GREEN + f"[+] BloodHound scan successfull! Output in {output_dir}" + Style.RESET_ALL)

