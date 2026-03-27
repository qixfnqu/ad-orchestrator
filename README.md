![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
# ADFlow

**ADFlow** is an automated Active Directory enumeration framework.  
It provides an interactive CLI tool for performing external reconnaissance and enumeration against Windows Active Directory environments. It centralizes session configuration, execution, and enumeration modules to streamline the discovery of AD metadata.

> ⚠️ This tool is intended for **authorized security testing only**. Do not use it against systems you do not own or have explicit permission to test.

---

## 🧠 Features

- Interactive command-line interface
- Session configuration for target, credentials, and enumeration options
- Supports both credentialed and non-credentialed enumeration workflows
- Displays collected data including users, hosts, credentials, and ports
- Modular command design for extensibility
- Desploys a Flask based local web UI for data visualization

---

## 🧾 Installation
   ```bash
   git clone https://github.com/qixfnqu/adflow.git
   cd adflow
   pip install -r requirements.txt
   python3 main.py
```
## 🚀 Usage
Once launched, you’ll see an interactive prompt:
```
➤ adflow [NoTarget 🛑] [NoDomain 🛑] [DC ❌] >
```
| Command                | Description                         |
| ---------------------- | ----------------------------------- |
| `set <option> <value>` | Set session configuration           |
| `show options`         | Show current configured options     |
| `show data`            | Show collected data                 |
| `run <value>`          | Start workflow                      |
| `config dc`            | Generate domain config (krb5/hosts) |
| `clear`                | Clear the terminal screen           |
| `help`                 | Show help menu                      |
| `exit` / `quit`        | Quit the program                    |

## 🧩 Session Configuration

Before scanning, configure session options:

```bash
adflow > set target <IP_OR_HOST>
adflow > set domain <DOMAIN>
adflow > set username <USERNAME>
adflow > set password <PASSWORD>
```
Use show options to view the current configuration.

## 🛠 Contributing

Contributions are welcome! Suggested improvements include:

- Adding support for additional enumeration modules
- Implementing automated reporting
- Improving session persistence
- Adding unit tests

## 📝 TODO
- Improve non-credentialed enumeration
- Improve credentialed enumeration
- Possibliy replace JSON session management to an SQL instance
- Add more modules
- Add the ability do modify session data from web UI

## ⚠️ Disclaimer

This tool is for ethical security testing only. Ensure you have explicit written authorization before performing any enumeration against a network or domain.
