"""ControlGit - Git account and repository settings management"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import base64
import requests


class GitHubAuth:
    """GitHub authentication handler"""

    def __init__(self, cred_file: Optional[str] = None):
        self.credentials = {}
        self.cred_file = cred_file or os.path.expanduser("~/.controlgit/credentials.json")
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

    def get_auth_header(self) -> Optional[str]:
        """Get Basic Auth header for GitHub API"""
        if not self.credentials.get("username") or not self.credentials.get("password"):
            return None

        auth_string = f"{self.credentials['username']}:{self.credentials['password']}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {encoded}"

    def get_token(self) -> Optional[str]:
        """Get GitHub token (password field)"""
        return self.credentials.get("password")

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


class ControlGit:
    """ControlGit - Comprehensive GitHub account and repository management"""

    def __init__(self, github_user: str = "abucodingai"):
        self.github_user = github_user
        self._github_auth = GitHubAuth()
        self.api_base = "https://api.github.com"
        
        # Import Redux store
        from .redux import ControlGitStore
        self.store = ControlGitStore(self)

    def _get_headers(self) -> Dict[str, str]:
        """Get GitHub API headers"""
        token = self._github_auth.get_token()
        if not token:
            print("❌ Not authenticated. Run 'controlgit auth set' first")
            return {}
        
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def auth(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        twofa: Optional[str] = None,
        extra: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set GitHub authentication credentials"""
        try:
            if not username or not password:
                self._gh_login()
                return
            
            self._github_auth.set_credentials(username, password, twofa, extra)
            print("✅ GitHub authentication configured")
        except Exception as e:
            print("Authentication Configuration Failed")

    def auth_status(self) -> None:
        """Show authentication status"""
        try:
            creds = self._github_auth.get_credentials()
            if not creds.get("username"):
                print("❌ Not authenticated")
                return

            print("✅ Authenticated")
            print(f"   Username: {creds.get('username')}")
            print(f"   2FA: {'Enabled' if creds.get('2fa') else 'Disabled'}")
        except Exception as e:
            print("Status Check Failed")

    def auth_clear(self) -> None:
        """Clear authentication credentials"""
        try:
            self._github_auth.clear_credentials()
            print("✅ Authentication cleared")
        except Exception as e:
            print("Clear Authentication Failed")

    # Account Settings Commands
    def settings(self) -> None:
        """Show account settings categories"""
        print("✅ Account Settings Categories:")
        print("   • General")
        print("   • Security")
        print("   • Notifications")
        print("   • Billing")
        print("   • Developer settings")
        print("\nUse: controlgit settings <category>")

    def list_settings(self) -> None:
        """List all account settings"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            response = requests.get(f"{self.api_base}/user", headers=headers)
            if response.status_code == 200:
                user = response.json()
                print("✅ Account Settings:")
                print(f"   Name: {user.get('name', 'N/A')}")
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Bio: {user.get('bio', 'N/A')}")
                print(f"   Location: {user.get('location', 'N/A')}")
                print(f"   Company: {user.get('company', 'N/A')}")
                print(f"   Blog: {user.get('blog', 'N/A')}")
                print(f"   Twitter: {user.get('twitter_username', 'N/A')}")
                print(f"   Public repos: {user.get('public_repos')}")
                print(f"   Followers: {user.get('followers')}")
                print(f"   Following: {user.get('following')}")
            else:
                print(f"❌ Failed to fetch settings: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def change_setting(self, setting_name: str, value: str) -> None:
        """Change account setting"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            data = {setting_name: value}
            response = requests.patch(f"{self.api_base}/user", headers=headers, json=data)
            if response.status_code == 200:
                print(f"✅ Setting '{setting_name}' updated to '{value}'")
            else:
                print(f"❌ Failed to update setting: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Token Management Commands
    def create_token(self, token_type: str, scopes: List[str]) -> None:
        """Create GitHub token (fine-grained or classic)"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            if token_type.lower() == "fine-grained":
                print("✅ Fine-grained token creation requires web interface")
                print("   Visit: https://github.com/settings/tokens?type=beta")
            elif token_type.lower() == "classic":
                data = {
                    "scopes": scopes,
                    "note": f"ControlGit token - {datetime.now().isoformat()}"
                }
                response = requests.post(
                    f"{self.api_base}/authorizations",
                    headers=headers,
                    json=data
                )
                if response.status_code == 201:
                    token_data = response.json()
                    print(f"✅ Classic token created")
                    print(f"   Token: {token_data.get('token')}")
                    print(f"   Scopes: {', '.join(token_data.get('scopes', []))}")
                else:
                    print(f"❌ Failed to create token: {response.status_code}")
            else:
                print("❌ Invalid token type. Use 'fine-grained' or 'classic'")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Repository Commands
    def repo_fork(self, repo_name: str) -> None:
        """Fork a repository"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            owner, repo = repo_name.split("/") if "/" in repo_name else (self.github_user, repo_name)
            response = requests.post(
                f"{self.api_base}/repos/{owner}/{repo}/forks",
                headers=headers
            )
            if response.status_code == 202:
                fork_data = response.json()
                print(f"✅ Repository forked")
                print(f"   Fork URL: {fork_data.get('html_url')}")
            else:
                print(f"❌ Failed to fork repository: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def repo_info(self, repo_name: str) -> None:
        """Show repository information"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            owner, repo = repo_name.split("/") if "/" in repo_name else (self.github_user, repo_name)
            response = requests.get(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=headers
            )
            if response.status_code == 200:
                repo_data = response.json()
                print(f"✅ Repository Information:")
                print(f"   Name: {repo_data.get('name')}")
                print(f"   Description: {repo_data.get('description', 'N/A')}")
                print(f"   URL: {repo_data.get('html_url')}")
                print(f"   Stars: {repo_data.get('stargazers_count')}")
                print(f"   Forks: {repo_data.get('forks_count')}")
                print(f"   Language: {repo_data.get('language', 'N/A')}")
                print(f"   Topics: {', '.join(repo_data.get('topics', []))}")
                print(f"   Private: {repo_data.get('private')}")
            else:
                print(f"❌ Failed to fetch repository info: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def repo_set_url(self, repo_name: str, custom_url: str) -> None:
        """Set custom repository URL (homepage)"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            owner, repo = repo_name.split("/") if "/" in repo_name else (self.github_user, repo_name)
            data = {"homepage": custom_url}
            response = requests.patch(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=headers,
                json=data
            )
            if response.status_code == 200:
                print(f"✅ Repository homepage set to: {custom_url}")
            else:
                print(f"❌ Failed to set URL: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def repo_issues(self, repo_name: str) -> None:
        """List repository issues"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            owner, repo = repo_name.split("/") if "/" in repo_name else (self.github_user, repo_name)
            response = requests.get(
                f"{self.api_base}/repos/{owner}/{repo}/issues",
                headers=headers
            )
            if response.status_code == 200:
                issues = response.json()
                if not issues:
                    print(f"✅ No issues found")
                    return
                
                print(f"✅ Repository Issues ({len(issues)}):")
                for issue in issues[:10]:  # Show first 10
                    print(f"   #{issue.get('number')}: {issue.get('title')}")
            else:
                print(f"❌ Failed to fetch issues: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def repo_fork_list(self, repo_name: str) -> None:
        """List repository forks"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            owner, repo = repo_name.split("/") if "/" in repo_name else (self.github_user, repo_name)
            response = requests.get(
                f"{self.api_base}/repos/{owner}/{repo}/forks",
                headers=headers
            )
            if response.status_code == 200:
                forks = response.json()
                if not forks:
                    print(f"✅ No forks found")
                    return
                
                print(f"✅ Repository Forks ({len(forks)}):")
                for fork in forks[:10]:  # Show first 10
                    print(f"   • {fork.get('full_name')} ({fork.get('stargazers_count')} stars)")
            else:
                print(f"❌ Failed to fetch forks: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def my_forks(self) -> None:
        """List my forked repositories"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            response = requests.get(
                f"{self.api_base}/user/repos?type=forks",
                headers=headers
            )
            if response.status_code == 200:
                repos = response.json()
                if not repos:
                    print(f"✅ No forked repositories found")
                    return
                
                print(f"✅ My Forked Repositories ({len(repos)}):")
                for repo in repos:
                    print(f"   • {repo.get('name')} ({repo.get('stargazers_count')} stars)")
            else:
                print(f"❌ Failed to fetch forks: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def my_pull_requests(self) -> None:
        """List my pull requests"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            response = requests.get(
                f"{self.api_base}/user/pulls",
                headers=headers
            )
            if response.status_code == 200:
                prs = response.json()
                if not prs:
                    print(f"✅ No pull requests found")
                    return
                
                print(f"✅ My Pull Requests ({len(prs)}):")
                for pr in prs:
                    print(f"   #{pr.get('number')}: {pr.get('title')} ({pr.get('state')})")
            else:
                print(f"❌ Failed to fetch pull requests: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def repo_config(self, repo_name: str, category: Optional[str] = None) -> None:
        """Show repository configuration by category"""
        headers = self._get_headers()
        if not headers:
            return
        
        try:
            owner, repo = repo_name.split("/") if "/" in repo_name else (self.github_user, repo_name)
            response = requests.get(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=headers
            )
            if response.status_code == 200:
                repo_data = response.json()
                
                categories = {
                    "General": {
                        "Name": repo_data.get('name'),
                        "Description": repo_data.get('description'),
                        "URL": repo_data.get('html_url'),
                        "Homepage": repo_data.get('homepage'),
                        "Language": repo_data.get('language'),
                    },
                    "Security": {
                        "Private": repo_data.get('private'),
                        "Has Wiki": repo_data.get('has_wiki'),
                        "Has Issues": repo_data.get('has_issues'),
                        "Has Downloads": repo_data.get('has_downloads'),
                    },
                    "Access": {
                        "Default Branch": repo_data.get('default_branch'),
                        "Allow Squash Merge": repo_data.get('allow_squash_merge'),
                        "Allow Merge Commit": repo_data.get('allow_merge_commit'),
                        "Allow Rebase Merge": repo_data.get('allow_rebase_merge'),
                    },
                    "Automation": {
                        "Archived": repo_data.get('archived'),
                        "Disabled": repo_data.get('disabled'),
                        "Topics": ', '.join(repo_data.get('topics', [])),
                    },
                    "Integrations": {
                        "Watchers": repo_data.get('watchers_count'),
                        "Stars": repo_data.get('stargazers_count'),
                        "Forks": repo_data.get('forks_count'),
                    }
                }
                
                if category and category in categories:
                    print(f"✅ {category} Settings for {repo_name}:")
                    for key, value in categories[category].items():
                        print(f"   {key}: {value}")
                else:
                    print(f"✅ Repository Configuration for {repo_name}:")
                    for cat, settings in categories.items():
                        print(f"\n   {cat}:")
                        for key, value in settings.items():
                            print(f"      {key}: {value}")
            else:
                print(f"❌ Failed to fetch repository config: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _gh_login(self) -> None:
        """Use GitHub CLI for interactive login"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("❌ GitHub CLI (gh) is not installed")
                print("Install it from: https://cli.github.com")
                return
            
            subprocess.run(["gh", "auth", "login"], check=False)
            print("✅ GitHub authentication configured via gh CLI")
        except FileNotFoundError:
            print("❌ GitHub CLI (gh) is not installed")
            print("Install it from: https://cli.github.com")
        except Exception as e:
            print(f"Authentication failed: {e}")

    def execute_command(self, command_line: str) -> str:
        """Execute a controlgit command via Redux store"""
        return self.store.execute_command(command_line)
    
    def get_state(self):
        """Get current Redux state"""
        return self.store.get_state()

