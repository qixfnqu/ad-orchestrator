#!/usr/bin/env python3

import os
import sys
import shlex

from colorama import init, Fore, Back, Style



from core import config_manager, enum

TOOL_NAME = "adflow"

def print_banner():
    banner = f"""
{Fore.YELLOW + Style.BRIGHT}     _   ___  ___ _    _____      __
    /_\\ |   \\| __| |  / _ \\ \\    / /
   / _ \\| |) | _|| |_| (_) \\ \\/\\/ / 
  /_/ \\_\\___/|_| |____\\___/ \\_/\\_/  
{Style.RESET_ALL}
{Fore.YELLOW + Style.DIM}                     adflow v0.1.0 (beta){Style.RESET_ALL}
"""
    print(banner)



class Session:
    def __init__(self):
        self.target = None
        self.domain = None
        self.username = None
        self.password = None
        self.dc_config = False
        self.data = {
            "users": [],
            "hosts": [],
            "creds": [],
            "ports": [],
            "services": [],
            "nmap_output" : "",
            "nmap_kerberos_output" : "",
            "smb_null_session": False,
            "smb_shares": [],
            "ldap_info" : "",
            "routes" : [],
            "subdomains" : []
        }

session = Session()


def cmd_set(args):
    if len(args) < 2:
        print("Usage: set <option> <value>")
        return

    key, value = args[0], args[1]

    if hasattr(session, key):
        setattr(session, key, value)
        print(f"[+] {key} => {value}")
    else:
        print(f"[-] Unknown option: {key}")


def cmd_show(args):
    if not args:
        print("Usage: show <options/data>")
        return

    key = args[0]

    if key == "options":
        print(Fore.CYAN + "\n[ Current Options ]\n")

        options = {
            "Target": session.target,
            "Domain": session.domain,
            "Username": session.username,
            "Password": session.password
        }

        for k, v in options.items():
            value = Fore.GREEN + v if v else Fore.RED + "Not set"
            print(f"{Fore.YELLOW}{k:<10}{Style.RESET_ALL} : {value}")

    elif key == "data":
        print(Fore.CYAN + "\n[ Collected Data ]\n")

        for k, v in session.data.items():
            label = f"{k:<20}"

            if isinstance(v, list):
                size = len(v)
                color = Fore.GREEN if size > 0 else Fore.RED
                print(f"{Fore.YELLOW}{label}{Style.RESET_ALL}: {color}{size} items")

            elif isinstance(v, dict):
                size = len(v)
                color = Fore.GREEN if size > 0 else Fore.RED
                print(f"{Fore.YELLOW}{label}{Style.RESET_ALL}: {color}{size} items")

            elif isinstance(v, set):
                size = len(v)
                color = Fore.GREEN if size > 0 else Fore.RED
                print(f"{Fore.YELLOW}{label}{Style.RESET_ALL}: {color}{size} items")

            elif isinstance(v, str):
                status = "set" if v else "empty"
                color = Fore.GREEN if v else Fore.RED
                print(f"{Fore.YELLOW}{label}{Style.RESET_ALL}: {color}{status}")

            else:
                print(f"{Fore.YELLOW}{label}{Style.RESET_ALL}: {Fore.RED if not v else Fore.GREEN}{v}")

    elif key in session.data:
        value = session.data[key]

        print(Fore.CYAN + f"\n[ {key.upper()} ]\n")

        if isinstance(value, list):
            if not value:
                print(Fore.RED + "No data")
            else:
                for i, item in enumerate(value, 1):
                    print(f"{Fore.YELLOW}[{i}] {item}")

        elif isinstance(value, dict):
            for k, v in value.items():
                print(f"{Fore.YELLOW}{k}{Style.RESET_ALL}: {v}")

        else:
            print(value)

    else:
        print(f"[-] Unknown show option: {key}")
        
    print("\n")


def cmd_run(args):
    if not args:
        print("Usage: run <init>")
        return

    os.system("clear")

    if args[0] == "init":
        print(Fore.CYAN + "\n[ Enumeration Mode ]\n")

        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Non-credentialed")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Credentialed")

        mode = input("\nSelect > ").strip()

        if mode == "1":
            enum.non_credentialed(session)
        elif mode == "2":
            enum.credentialed(session)
        else:
            print(Fore.RED + "Invalid option")

def cmd_config(args):
    if not args:
        print("Usage: config <host/dc>")    
        return  
  
    if args[0] == "dc":
        if session.target is None or session.domain is None: 
            print("[-] Establish a valid target and domain")
            return

        dc_ip = session.target
        domain = session.domain.lower()
    
        config_manager.generate_krb5(domain, dc_ip)
        session.dc_config = True

        choice = input("Do you want to modify /etc/hosts? (Y/N) ").lower()
        

        if choice == "y":
            config_manager.generate_etc_hosts(dc_ip, domain, True)

        elif choice == "n":
            print("[-] /etc/hosts not modified")
            return
        else: 
            print("[-] Invalid option")
            print("[-] /etc/hosts not modified")
            return

        

        

    if args[0] == "host":
        pass

def cmd_clear(args):
    os.system("clear")


def cmd_exit(args):
    print("Exiting...")
    sys.exit(0)


def cmd_help(args):
    print("""
Available commands:

  config <host/dc>       Set current target as DC/Host
  set <option> <value>   Set session value
  show options           Show current config
  show data              Show collected data
  run <init/web>         Execute workflow
  clear                  Clear screen
  help                   Show this help
  exit                   Quit

""")


COMMANDS = {
    "set": cmd_set,
    "show": cmd_show,
    "run": cmd_run,
    "clear": cmd_clear,
    "exit": cmd_exit,
    "quit" : cmd_exit,
    "help": cmd_help,
    "config": cmd_config
}

def get_prompt():
    target_status = (Fore.GREEN + "[" + session.target + "]") if session.target else (Fore.RED + "[NoTarget 🛑]")
    
    domain_status = (Fore.GREEN + "[" + session.domain + "]") if session.domain else (Fore.RED + "[NoDomain 🛑]")
    
    dc_status = (Fore.GREEN + "[DC ✅]") if session.dc_config else (Fore.RED + "[DC ❌]")
    
    last_action = getattr(session, "last_action_status", "")
    if last_action == "ok":
        action_symbol = Fore.GREEN + "⚡"
    elif last_action == "fail":
        action_symbol = Fore.RED + "❌"
    else:
        action_symbol = Fore.CYAN + "➤"
    
    prompt = f"{action_symbol} {Fore.CYAN}{TOOL_NAME.lower()}{Style.RESET_ALL} {target_status} {domain_status} {dc_status} > {Style.RESET_ALL}"
    return prompt


def main():
    init(autoreset=True)
    os.system("clear")
    print_banner()

    while True:
        try:
            prompt = get_prompt()
            user_input = input(prompt)

            if not user_input.strip():
                continue

            parts = shlex.split(user_input)
            command = parts[0]
            args = parts[1:]

            if command in COMMANDS:
                COMMANDS[command](args)
            else:
                print(f"[-] Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")


if __name__ == "__main__":
    main()
