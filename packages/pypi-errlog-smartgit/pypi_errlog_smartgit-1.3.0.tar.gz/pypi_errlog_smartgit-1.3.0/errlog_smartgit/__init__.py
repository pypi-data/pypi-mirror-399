"""errlog-smartgit - SmartGit Error Handler"""

__version__ = "1.1.0"
__author__ = "Abu Shariff"

from .errlog_smartgit import SmartGitErr

# Check for GitHub CLI on first import
import os
import subprocess

_gh_check_done = False

def _check_gh_cli():
    """Check if GitHub CLI is installed, install if missing"""
    global _gh_check_done
    if _gh_check_done:
        return
    _gh_check_done = True
    
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return  # gh is installed
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # gh is not installed, try to install it
    try:
        from .post_install import install_gh
        install_gh()
    except Exception:
        pass  # Silently fail, user can install manually

# Run check on import
_check_gh_cli()

__all__ = ["SmartGitErr"]
