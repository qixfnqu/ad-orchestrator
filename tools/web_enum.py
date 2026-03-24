import subprocess
from colorama import Fore, Back, Style
from core import aux


def basic_web_enum(target, use_https=False):
	proto = "https" if use_https else "http"
	print(f"[+] Target: {proto}://{target}")


	print("[+] Running WhatWeb...")
	cmd = f"whatweb {proto}://{target}"

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

def fuzz(target, use_https, wordlist):
	proto = "https" if use_https else "http"
	url = f"{proto}://{target}"
	cmd = f"gobuster dir -u {url} -w {wordlist} -q"

	print("\n[+] Executing gobuster (Ctrl + C to stop)")
	process = None

	routes = []

	try:
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
			routes.append(f"{url}/{line.split()[0].strip()}")

	except KeyboardInterrupt:
		if process:
			process.terminate()
			process.wait()

		print("\n")
		return routes

	return routes


def subdomain_discovery(target, domain, mode, wordlist, use_https=False):
	proto = "https" if use_https else "http"

	cmd = ""
	print("\n")
	if mode == "normal":
		cmd = f"subfinder -d {domain} -silent"
		print(f"[+] Searching subdomains for {proto}://{target}")
	elif mode == "vhost":
		cmd = f"ffuf -u {proto}://{target} -H \"Host: FUZZ.{domain}\" -w {wordlist} -ac"
		print(f"[+] Searching vHosts for {proto}://{target}")
		print("Press Ctrl + C to stop")

	process = None

	try:
		process = subprocess.Popen(
			cmd,
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True
		)

		output = ""
		subdomains = []
		for line in process.stdout:
			line = aux.strip_ansi(line).strip()

			if not line:
				continue

			if mode == "normal":
				print(line)
				subdomains.append(line)
				continue

			if line.startswith(("/", "_", "v", "::")):
				continue

			if any(x in line for x in ["Method", "URL", "Wordlist", "Header", "Threads", "Matcher", "Timeout", "Calibration", "Follow redirects"]):
				continue

			if "[Status:" in line:
				print(line)

				sub = line.split()[0]
				print(Fore.GREEN + f"[+] SUBDOMAIN FOUND: {sub.strip()}")
				print(Style.RESET_ALL)

				full_domain = f"{sub}.{domain}"
				subdomains.append(full_domain)
	except KeyboardInterrupt:
		if process:
			process.terminate()
			process.wait()

			print("\n")
			return list(subdomains)	
	
	return list(subdomains)

def fingerprint_version(target, use_https=False):
	proto = "https" if use_https else "http"

	url = f"{proto}://{target}"
	cmd = f"curl -sL {url} | grep version"

	print(f"\n[+] Trying to find software versions on {url}")

	process = subprocess.Popen(
		cmd,
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True
	)

	output = ""

	for line in process.stdout:
		print(Fore.GREEN + f"Found possible version: {line.strip()}", end="")
		print(Style.RESET_ALL)
		output += line

	return output