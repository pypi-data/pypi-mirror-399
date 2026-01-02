"""Post-install script to check and install GitHub CLI"""

import subprocess
import sys
import platform
import os


def run_batch_file() -> bool:
    """Run the batch file to install GitHub CLI"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file = os.path.join(script_dir, "install_gh.bat")
        
        if not os.path.exists(batch_file):
            print(f"❌ Batch file not found: {batch_file}")
            return False
        
        # Run the batch file
        result = subprocess.run(
            [batch_file],
            shell=True,
            capture_output=False
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running batch file: {e}")
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
    print("ControlGit Post-Install Setup")
    print("="*60 + "\n")
    
    # Check if gh is already installed
    if check_gh_installed():
        print("✅ GitHub CLI (gh) is already installed")
        print("\nNext step: Run 'gh auth login' to authenticate with GitHub")
        print("="*60 + "\n")
        return
    
    print("⚠️  GitHub CLI (gh) is not installed")
    print("ControlGit requires GitHub CLI for authentication\n")
    
    # Run the batch file to install
    if run_batch_file():
        print("\n✅ Setup complete!")
        print("Next step: Run 'gh auth login' to authenticate with GitHub")
    else:
        print("\n⚠️  Please install GitHub CLI manually:")
        print("   https://cli.github.com")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    post_install()
