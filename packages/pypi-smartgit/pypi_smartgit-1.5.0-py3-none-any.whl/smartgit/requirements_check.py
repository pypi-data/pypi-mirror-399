"""Check system requirements for SmartGit"""

import subprocess
import sys
from typing import Tuple


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
    print("SmartGit System Requirements Check")
    print("="*60 + "\n")
    
    all_ok = True
    
    # Check Git
    git_ok, git_msg = check_git()
    status = "✅" if git_ok else "❌"
    print(f"{status} Git: {git_msg}")
    if not git_ok:
        print("   Install from: https://git-scm.com")
        all_ok = False
    
    # Check GitHub CLI
    gh_ok, gh_msg = check_gh_cli()
    status = "✅" if gh_ok else "❌"
    print(f"{status} GitHub CLI (gh): {gh_msg}")
    if not gh_ok:
        print("   Install from: https://cli.github.com")
        print("   Windows: choco install gh")
        print("   macOS: brew install gh")
        print("   Linux: https://cli.github.com/manual/installation")
        all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ All requirements satisfied!")
        print("\nNext step: Run 'gh auth login' to authenticate with GitHub")
    else:
        print("❌ Some requirements are missing. Please install them.")
    print("="*60 + "\n")
    
    return all_ok


if __name__ == "__main__":
    check_all_requirements()
