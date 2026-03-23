import subprocess
import re

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

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
	cmd = f"gobuster dir -u {proto}://{target} -w {wordlist} -q"

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

def subdomain_discovery(target, domain, mode, wordlist, use_https=False):
	proto = "https" if use_https else "http"

	cmd = ""
	if mode == "normal":
		cmd = f"subfinder -d {domain} -silent"
		print(f"[+] Searching subdomains for {proto}://{target}")
	elif mode == "vhost":
		cmd = f"ffuf -u {proto}://{target} -H \"Host: FUZZ.{domain}\" -w {wordlist} -ac"
		print(f"[+] Searching vHosts for {proto}://{target}")

	print(f"[+] CMD: {cmd}")

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
		line = strip_ansi(line).strip()

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
			print(f"[+] SUBDOMAIN FOUND: {sub.strip()}")

			full_domain = f"{sub}.{domain}"
			subdomains.append(full_domain)

	process.wait()
	return list(subdomains)
