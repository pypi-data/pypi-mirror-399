"""Post-install script to check and install GitHub CLI"""

import subprocess
import sys
import platform
import os
from colorama import Fore, Style, init

init(autoreset=True)


def run_batch_file() -> bool:
    """Run the batch file to install GitHub CLI"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file = os.path.join(script_dir, "install_gh.bat")
        
        if not os.path.exists(batch_file):
            print(f"{Fore.RED}❌ Batch file not found: {batch_file}{Style.RESET_ALL}")
            return False
        
        # Run the batch file
        result = subprocess.run(
            [batch_file],
            shell=True,
            capture_output=False
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"{Fore.RED}❌ Error running batch file: {e}{Style.RESET_ALL}")
        return False


def check_gh_installed() -> bool:
    """Check if GitHub CLI is installed"""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def post_install():
    """Run post-install checks and installations"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}errlog-smartgit Post-Install Setup{Style.RESET_ALL}")
    print("="*60 + "\n")
    
    # Check if gh is already installed
    if check_gh_installed():
        print(f"{Fore.GREEN}✅ GitHub CLI (gh) is already installed{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next step: Run 'gh auth login' to authenticate with GitHub{Style.RESET_ALL}")
        print("="*60 + "\n")
        return
    
    print(f"{Fore.YELLOW}⚠️  GitHub CLI (gh) is not installed{Style.RESET_ALL}")
    print("errlog-smartgit requires GitHub CLI for authentication\n")
    
    # Run the batch file to install
    if run_batch_file():
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Setup complete!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Next step: Run 'gh auth login' to authenticate with GitHub{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Please install GitHub CLI manually:{Style.RESET_ALL}")
        print("   https://cli.github.com")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    post_install()

