"""Check system requirements for errlog-smartgit"""

import subprocess
import sys
from typing import Tuple
from colorama import Fore, Style, init

init(autoreset=True)


def check_git() -> Tuple[bool, str]:
    """Check if git is installed"""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, "Git not found"
    except FileNotFoundError:
        return False, "Git not found"


def check_gh_cli() -> Tuple[bool, str]:
    """Check if GitHub CLI is installed"""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, "GitHub CLI not found"
    except FileNotFoundError:
        return False, "GitHub CLI not found"


def check_all_requirements() -> bool:
    """Check all system requirements"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}errlog-smartgit System Requirements Check{Style.RESET_ALL}")
    print("="*60 + "\n")
    
    all_ok = True
    
    # Check Git
    git_ok, git_msg = check_git()
    status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if git_ok else f"{Fore.RED}❌{Style.RESET_ALL}"
    print(f"{status} Git: {git_msg}")
    if not git_ok:
        print(f"   {Fore.YELLOW}Install from: https://git-scm.com{Style.RESET_ALL}")
        all_ok = False
    
    # Check GitHub CLI
    gh_ok, gh_msg = check_gh_cli()
    status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if gh_ok else f"{Fore.RED}❌{Style.RESET_ALL}"
    print(f"{status} GitHub CLI (gh): {gh_msg}")
    if not gh_ok:
        print(f"   {Fore.YELLOW}Install from: https://cli.github.com{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}Windows: choco install gh{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}macOS: brew install gh{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}Linux: https://cli.github.com/manual/installation{Style.RESET_ALL}")
        all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ All requirements satisfied!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next step: Run 'gh auth login' to authenticate with GitHub{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}❌ Some requirements are missing. Please install them.{Style.RESET_ALL}")
    print("="*60 + "\n")
    
    return all_ok


if __name__ == "__main__":
    check_all_requirements()
