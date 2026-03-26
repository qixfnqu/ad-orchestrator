import subprocess
from colorama import Fore, Back, Style
from core import aux
from core.config import PORT_SERVICE_MAP

import re
import requests


def basic_web_enum(target, use_https=False):
	proto = "https" if use_https else "http"
	print(f"[+] Target: {proto}://{target}")


	print("[+] Running WhatWeb...")
	cmd = ["whatweb", f"{proto}://{target}"]

	output = aux.run_command(cmd)
	return output

def fuzz(target, use_https, wordlist):
	proto = "https" if use_https else "http"
	url = f"{proto}://{target}"
	cmd = [
    	"gobuster", "dir",
    	"-u", url,
    	"-w", wordlist,
    	"-q"
	]

	print("\n[+] Executing gobuster (Ctrl + C to stop)")
	process = None

	routes = []

	try:
		process = subprocess.Popen(
			cmd,
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
		print(Fore.GREEN + f"[+] Found {len(routes)} route(s)" + Style.RESET_ALL)		
		return routes

	print(Fore.GREEN + f"[+] Found {len(routes)} route(s)")
	return routes


def subdomain_discovery(target, domain, mode, wordlist, use_https=False):
	proto = "https" if use_https else "http"

	cmd = ""
	print("\n")
	if mode == "normal":
		cmd = ["subfinder", "-d", domain, "-silent"]
		print(f"[+] Searching subdomains for {proto}://{target}")

	elif mode == "vhost":
		cmd = [
    		"ffuf",
    		"-u", f"{proto}://{target}",
    		"-H", f"Host: FUZZ.{domain}",
    		"-w", wordlist,
    		"-ac"
		]
		print(f"[+] Searching vHosts for {proto}://{target}")
		print("Press Ctrl + C to stop")

	process = None

	try:
		process = subprocess.Popen(
			cmd,
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
			print(Fore.GREEN + f"[+] Found {len(subdomains)} subdomain(s)" + Style.RESET_ALL)
			return list(subdomains)	
	
	print(Fore.GREEN + f"[+] Found {len(subdomains)} subdomain(s)" + Style.RESET_ALL)
	return list(subdomains)

def fingerprint_version(target, use_https=False):
    proto = "https" if use_https else "http"
    base_url = f"{proto}://{target}"
    
    print(f"\n[+] Advanced fingerprinting on {base_url}")
    
    version_patterns = {
        'Apache': [
            r'Apache/(\d+\.\d+\.?\d*)',
            r'Server: Apache/(\d+\.\d+\.?\d*)'
        ],
        'Nginx': [
            r'nginx/(\d+\.\d+\.?\d*)',
            r'Server: nginx/(\d+\.\d+\.?\d*)'
        ],
        'IIS': [
            r'IIS/(\d+\.\d+)',
            r'Server: Microsoft-IIS/(\d+\.\d+)'
        ],
        'PHP': [
            r'PHP/(\d+\.\d+\.?\d*)',
            r'X-Powered-By: PHP/(\d+\.\d+\.?\d*)'
        ],
        'Node.js': [
            r'node\.js/(\d+\.\d+\.?\d*)',
            r'X-Powered-By: Express'
        ],
        'WordPress': [
            r'wp-content',
            r'generator" content="WordPress (\d+\.\d+(?:\.\d+)?)'
        ],
        'Drupal': [
            r'drupal\.js',
            r'Generator: Drupal (\d+)'
        ],
        'Joomla': [
            r'Joomla!',
            r'/administrator/'
        ]
    }
    
    results = {}
    
    try:
        print(f"  └─ Checking server headers...")
        response = requests.get(base_url, verify=False)
        
        server_header = response.headers.get('Server', '')
        x_powered_by = response.headers.get('X-Powered-By', '')
        generator = response.headers.get('X-Generator', '')
        
        headers_to_check = [server_header, x_powered_by, generator]
        
        for software, patterns in version_patterns.items():
            for header in headers_to_check:
                for pattern in patterns:
                    match = re.search(pattern, header, re.IGNORECASE)
                    if match:
                        version = match.group(1) if match.groups() else "detected"
                        results[software] = version
                        print(f"  ├─ {Fore.GREEN}{software}: {version}{Style.RESET_ALL}")
                        break
    except Exception as e:
        print(f"  └─ Headers check failed: {e}")
    
    common_paths = [
        '/', '/robots.txt', '/sitemap.xml', '/wp-admin/', '/admin/',
        '/server-status', '/phpinfo.php', '/.env'
    ]
    
    for path in common_paths:
        try:
            url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
            print(f"  └─ Probing {path}...")
            
            response = requests.get(url, timeout=timeout//2, verify=False)
            
            content = response.text.lower()
            for software, patterns in version_patterns.items():
                if software in results: 
                    continue
                    
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        version = matches[0] if matches else "detected"
                        results[software] = version
                        print(f"  ├─ {Fore.GREEN}{software}: {version} (path: {path}){Style.RESET_ALL}")
                        break
                        
        except:
            continue
    
    try:
        cmd = ["whatweb", "-q", "-U", base_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.stdout.strip():
            print(f"  └─ WhatWeb: {Fore.CYAN}{result.stdout.strip()}{Style.RESET_ALL}")
    except:
        pass
    
    # Resumen final
    if results:
        print(f"\n{Fore.YELLOW}[*] Summary:{Style.RESET_ALL}")
        for software, version in results.items():
            print(f"    {software}: {version}")
        return results
    else:
        print(f"{Fore.RED}[!] No versions detected{Style.RESET_ALL}")
        return {}