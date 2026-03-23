#!/usr/bin/env python3

import os
import sys
import shlex



from core import config_manager, enum

TOOL_NAME = "Orchestrator"

def print_banner():
    banner = f"""
=====================================
           AD Orchestrator           
=====================================
 Automated AD Enumeration Framework  
====================================="""
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
            "nmap_output" : "",
            "nmap_kerberos_output" : "",
            "smb_null_session": False,
            "smb_shares": [],
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
        print("\n[ Current options ]\n")
        print(f"target   : {session.target}")
        print(f"domain   : {session.domain}")
        print(f"username : {session.username}")
        print(f"password : {session.password}")

    elif key == "data":
        print("\n[ Collected Data ]")
        for k, v in session.data.items():
            if isinstance(v, (list, dict) ):
                size = len(v)
                print(f"{k} : [{size if size > 0 else 'empty'}]")
            else:    
                print(f"{k}")

    elif key in session.data:
        print(f"\n[ {key} ]\n")

        value = session.data[key]

        if isinstance(value, list):
            for item in value:
                print(item)

        elif isinstance(value, dict):
            for k, v in value.items():
                print(f"{k}: {v}")

        else:
            print(value)

    else:
        print(f"[-] Unknown show option: {key}")
        
    print("\n")


def cmd_run(args):
    os.system("clear")
    print("\n[+] Starting interactive run\n")

    
    print("[?] Select enumeration mode:")
    print("    1) Non-credentialed")
    print("    2) Credentialed")

    mode = input("> ").strip()

    if mode == "1":
        enum.non_credentialed(session)
    elif mode == "2":
        enum.credentialed(session)
    else:
        print("[-] Invalid option")

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
  run                    Execute workflow
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


def main():
    os.system("clear")
    print_banner()

    while True:
        try:
            prompt = f"{TOOL_NAME.lower()} > "
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
