import subprocess
from colorama import Fore, Back, Style


def parse_smb_shares(output):
    shares = []
    parsing = False

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("Sharename"):
            parsing = True
            continue

        if parsing and line.startswith("----"):
            continue
        
        if parsing and line == "":
            break

        if parsing:
            parts = line.split()
  
            if len(parts) >= 2:
                share = parts[0]
                share_type = parts[1]

                
                if share_type in ["Disk", "IPC", "Printer"]:
                    shares.append(share)

    print(Fore.GREEN + f"[+] Found {len(shares)} shares")
    return shares



def list_shares(target, username="", password=""):
	if username == "" or password == "":
		cmd = ["smbclient", "-L", f"\\\\{target}\\", "-N"]


	process = subprocess.run(
		cmd,
		capture_output=True,
 		text=True
	)

	output = ""
	for line in process.stdout:
		print(line, end="")
		output += line

	shares = parse_smb_shares(output)
	return shares