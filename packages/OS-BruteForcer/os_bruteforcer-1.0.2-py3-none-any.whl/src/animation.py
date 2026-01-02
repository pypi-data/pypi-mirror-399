import subprocess
import time
from termcolor import colored
def banner():
    try:
        result = subprocess.run(
            ["figlet", "OS Bruteforcer"],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            print(colored(line,'blue'))
            time.sleep(0.05)
        author = "<< Author: cyb2rS2c >>"
        print(colored(author,'red'))
        time.sleep(0.03)
        print()

    except FileNotFoundError:
        print(colored("=== OS Bruteforcer ===",'blue'))
        print(colored("<< Author: cyb2rS2c >>",'red'))
