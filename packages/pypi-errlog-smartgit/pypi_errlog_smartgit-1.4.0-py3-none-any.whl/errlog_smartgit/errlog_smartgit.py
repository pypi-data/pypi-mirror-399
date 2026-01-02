"""SmartGit Error Handler with detailed feedback"""

import subprocess
import sys
import json
import os
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class GitHubAuth:
    """GitHub authentication handler"""

    def __init__(self, cred_file: Optional[str] = None):
        self.credentials = {}
        self.cred_file = cred_file or os.path.expanduser("~/.smartgit/credentials.json")
        self._load_credentials()

    def set_credentials(
        self,
        username: str,
        password: str,
        twofa: Optional[str] = None,
        extra: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set GitHub credentials"""
        self.credentials = {
            "username": username,
            "password": password,
            "2fa": twofa,
            "extra": extra or {},
        }
        self._save_credentials()

    def _load_credentials(self) -> None:
        """Load credentials from file"""
        try:
            if os.path.exists(self.cred_file):
                with open(self.cred_file, "r") as f:
                    self.credentials = json.load(f)
        except Exception:
            self.credentials = {}

    def _save_credentials(self) -> None:
        """Save credentials to file"""
        try:
            cred_dir = os.path.dirname(self.cred_file)
            os.makedirs(cred_dir, exist_ok=True)
            with open(self.cred_file, "w") as f:
                json.dump(self.credentials, f)
            # Set restrictive permissions on Unix-like systems
            if hasattr(os, 'chmod'):
                os.chmod(self.cred_file, 0o600)
        except Exception:
            pass

    def get_auth_header(self) -> Optional[str]:
        """Get Basic Auth header for GitHub API"""
        if not self.credentials.get("username") or not self.credentials.get("password"):
            return None

        auth_string = f"{self.credentials['username']}:{self.credentials['password']}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {encoded}"

    def get_credentials(self) -> Dict[str, Any]:
        """Get stored credentials"""
        return self.credentials

    def clear_credentials(self) -> None:
        """Clear stored credentials"""
        self.credentials = {}
        try:
            if os.path.exists(self.cred_file):
                os.remove(self.cred_file)
        except Exception:
            pass

    def has_2fa(self) -> bool:
        """Check if 2FA is configured"""
        return bool(self.credentials.get("2fa"))

    def get_2fa(self) -> Optional[str]:
        """Get 2FA code"""
        return self.credentials.get("2fa")


class SmartGitErr:
    """SmartGit Error Handler - provides detailed feedback"""

    def __init__(self, path: Optional[str] = None, github_user: str = "abucodingai"):
        import os
        self.path = os.path.abspath(path or os.getcwd()) if path else None
        self.github_user = github_user
        self.process_log = None
        self._github_auth = GitHubAuth()
        
        # Import and initialize ControlGit
        try:
            from controlgit import ControlGit as ControlGitClass
            self.controlgit = ControlGitClass(github_user=github_user)
        except ImportError:
            self.controlgit = None
        
        # Validate path if provided
        if self.path and not os.path.isdir(self.path):
            raise ValueError(f"Path does not exist or is not a directory: {self.path}")

    def all(self, no_version: bool = False, no_deploy: bool = False) -> None:
        """Complete workflow with detailed feedback"""
        args = []
        if no_version:
            args.append("-no-version")
        if no_deploy:
            args.append("-no-deploy")

        self._execute_command("smartgit all", args, 10)

    def repo(self, project_name: str) -> None:
        """Create repository with detailed feedback"""
        self._execute_command(f"smartgit repo {project_name}", [], 3)

    def ignore(self, files: List[str]) -> None:
        """Ignore files with detailed feedback"""
        self._execute_command(f"smartgit ignore {', '.join(files)}", [], 2)

    def include(self, files: List[str]) -> None:
        """Include files with detailed feedback"""
        self._execute_command(f"smartgit include {', '.join(files)}", [], 2)

    def version(
        self, project_name: str, version_name: str, files: Optional[List[str]] = None
    ) -> None:
        """Create version with detailed feedback"""
        self._execute_command(
            f"smartgit version {project_name} {version_name}", [], 3
        )

    def addfile(
        self, project_name: str, version_name: str, files: List[str]
    ) -> None:
        """Add files to version with detailed feedback"""
        self._execute_command(
            f"smartgit addfile {project_name} {version_name}", [], 3
        )

    def lab(self, project_name: Optional[str] = None) -> None:
        """Activate GitLab mode with detailed feedback"""
        self._execute_command(f"smartgit lab {project_name or ''}", [], 2)

    def shortcut(self, shortcut_name: str, command: str) -> None:
        """Create shortcut with detailed feedback"""
        self._execute_command(f"smartgit shortcut {shortcut_name}", [], 3)

    def auth(self, username: Optional[str] = None, password: Optional[str] = None, twofa: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> None:
        """Set GitHub authentication with detailed feedback"""
        self._start_process("smartgit auth set", 2)
        self._log_step(1, f"Configuring authentication")
        
        # If no credentials provided, use gh CLI login
        if not username or not password:
            self._gh_login()
            return
        
        self._github_auth.set_credentials(username, password, twofa, extra)
        self._log_step(2, "Authentication configured")
        print(f"{Fore.GREEN}✅ GitHub authentication configured{Style.RESET_ALL}")

    def _gh_login(self) -> None:
        """Use GitHub CLI for interactive login"""
        try:
            # Check if gh CLI is installed
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"{Fore.RED}❌ GitHub CLI (gh) is not installed{Style.RESET_ALL}")
                print("Install it from: https://cli.github.com")
                return
            
            # Run gh auth login
            subprocess.run(["gh", "auth", "login"], check=False)
            print(f"{Fore.GREEN}✅ GitHub authentication configured via gh CLI{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}❌ GitHub CLI (gh) is not installed{Style.RESET_ALL}")
            print("Install it from: https://cli.github.com")
        except Exception as e:
            print(f"{Fore.RED}Authentication failed: {e}{Style.RESET_ALL}")

    def auth_status(self) -> None:
        """Show authentication status with detailed feedback"""
        self._start_process("smartgit auth status", 1)
        self._log_step(1, "Checking authentication status")
        creds = self._github_auth.get_credentials()
        if not creds.get("username"):
            print(f"{Fore.RED}❌ Not authenticated{Style.RESET_ALL}")
            return
        print(f"{Fore.GREEN}✅ Authenticated{Style.RESET_ALL}")
        print(f"   Username: {creds.get('username')}")
        print(f"   2FA: {'Enabled' if creds.get('2fa') else 'Disabled'}")
        if creds.get("extra"):
            print(f"   Extra: {len(creds.get('extra'))} fields")

    def auth_clear(self) -> None:
        """Clear authentication with detailed feedback"""
        self._start_process("smartgit auth clear", 1)
        self._log_step(1, "Clearing authentication")
        self._github_auth.clear_credentials()
        print(f"{Fore.GREEN}✅ Authentication cleared{Style.RESET_ALL}")

    def _execute_command(
        self, command: str, args: List[str], total_steps: int
    ) -> None:
        """Execute command with detailed error handling"""
        self._start_process(command, total_steps)

        try:
            for i in range(1, total_steps + 1):
                self._log_step(i, f"Executing step {i}/{total_steps}")

            # Execute the actual smartgit command
            full_command = f"{command} {' '.join(args)}".strip()
            result = subprocess.run(
                full_command, shell=True, capture_output=False, text=True
            )

            self._end_process(result.returncode == 0)
            if result.returncode == 0:
                self._print_success()
            else:
                self._print_error(f"Command failed with code {result.returncode}")
        except Exception as error:
            self._end_process(False)
            self._print_error(str(error))

    def _start_process(self, command: str, total_steps: int) -> None:
        """Start process logging"""
        self.process_log = {
            "command": command,
            "start_time": datetime.now(),
            "steps": [],
            "success": False,
            "total_duration": 0,
        }

        print(f"\n{Fore.CYAN}{Style.BRIGHT}▶ {command}{Style.RESET_ALL}")
        print(f"{Style.DIM}Total steps: {total_steps}{Style.RESET_ALL}\n")

    def _log_step(self, step_number: int, message: str) -> None:
        """Log a step"""
        if not self.process_log:
            return

        self.process_log["steps"].append(
            {
                "step": step_number,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )

        progress = f"[{step_number}/{len(self.process_log['steps'])}]"
        print(f"{Fore.BLUE}{progress}{Style.RESET_ALL} {Style.DIM}{message}{Style.RESET_ALL}")

    def _end_process(self, success: bool) -> None:
        """End process logging"""
        if not self.process_log:
            return

        end_time = datetime.now()
        self.process_log["success"] = success
        self.process_log["total_duration"] = (
            end_time - self.process_log["start_time"]
        ).total_seconds() * 1000

    def _print_success(self) -> None:
        """Print success message"""
        if not self.process_log:
            return

        print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ Success{Style.RESET_ALL}")
        print(
            f"{Style.DIM}Completed in {self.process_log['total_duration']:.0f}ms{Style.RESET_ALL}\n"
        )

    def _print_error(self, error_message: str) -> None:
        """Print error message"""
        if not self.process_log:
            return

        print(f"\n{Fore.RED}{Style.BRIGHT}✗ Error{Style.RESET_ALL}")
        print(f"{Fore.RED}{error_message}{Style.RESET_ALL}")
        print(
            f"{Style.DIM}Failed after {self.process_log['total_duration']:.0f}ms{Style.RESET_ALL}\n"
        )

    def controlgit_command(self, command_line: str) -> str:
        """Execute a ControlGit command with detailed feedback"""
        if not self.controlgit:
            return "❌ ControlGit not available. Install pypi-controlgit"
        
        try:
            result = self.controlgit.execute_command(command_line)
            print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
            return result
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
