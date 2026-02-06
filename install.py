#!/usr/bin/env python3

import os
import sys
import subprocess

def run(cmd):
    print(f"[+] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    if os.geteuid() != 0:
        print("[-] Please run this installer as root:")
        print("    sudo python3 install.py")
        sys.exit(1)

    print("\n[+] Installing system dependencies for packet capture tool\n")

    # Detect package manager
    if os.path.exists("/usr/bin/apt"):
        run("apt update")
        run("apt install -y tshark")
    elif os.path.exists("/usr/bin/pacman"):
        run("pacman -Sy --noconfirm wireshark-cli")
    elif os.path.exists("/usr/bin/dnf"):
        run("dnf install -y wireshark-cli")
    else:
        print("[-] Unsupported Linux distribution")
        sys.exit(1)

    # Set capabilities for tshark
    tshark_path = subprocess.check_output("which tshark", shell=True).decode().strip()
    run(f"setcap cap_net_raw,cap_net_admin=eip {tshark_path}")

    # Create captures directory
    if not os.path.exists("captures"):
        os.makedirs("captures")
        print("[+] Created captures/ directory")

    print("\n[✓] Installation complete")
    print("\nYou can now run the tool using:")
    print("  sudo python3 capture.py")
    print("or (after capability set):")
    print("  python3 capture.py\n")

if __name__ == "__main__":
    main()
