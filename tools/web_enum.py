import subprocess

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
