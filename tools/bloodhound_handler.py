import subprocess
import os

from colorama import Fore, Back, Style
from core import aux


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
		output = aux.run_command(cmd, output_dir)

	except Exception as e:
		print(Fore.RED + f"[-] BloodHound scan failed with: {e}" + Style.RESET_ALL)
		return

	print(Fore.GREEN + f"[+] BloodHound scan successfull! Output in {output_dir}" + Style.RESET_ALL)

