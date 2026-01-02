"""ControlGit CLI interface"""

import sys
import json
from .controlgit import ControlGit


def main():
    """Main CLI entry point"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    # Check for global commands first
    global_commands = ["auth", "settings", "list-settings", "change-setting", "create-token", "my-forks", "my-pull-requests", "help"]
    
    first_arg = sys.argv[1]
    
    try:
        controlgit = ControlGit(github_user="abucodingai")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Handle global commands
        if first_arg == "auth":
            if len(sys.argv) < 3:
                print("Usage: controlgit auth <set|status|clear> [username] [token]")
                return
            
            auth_cmd = sys.argv[2]
            if auth_cmd == "set":
                username = sys.argv[3] if len(sys.argv) > 3 else None
                token = sys.argv[4] if len(sys.argv) > 4 else None
                controlgit.auth(username, token)
            elif auth_cmd == "status":
                controlgit.auth_status()
            elif auth_cmd == "clear":
                controlgit.auth_clear()
            else:
                print("Usage: controlgit auth <set|status|clear>")
        
        elif first_arg == "settings":
            category = sys.argv[2] if len(sys.argv) > 2 else None
            if category:
                print(f"Settings for category: {category}")
            else:
                controlgit.settings()
        
        elif first_arg == "list-settings":
            controlgit.list_settings()
        
        elif first_arg == "change-setting":
            if len(sys.argv) < 4:
                print("Usage: controlgit change-setting <setting-name> <value>")
                return
            setting_name = sys.argv[2]
            value = sys.argv[3]
            controlgit.change_setting(setting_name, value)
        
        elif first_arg == "create-token":
            if len(sys.argv) < 4:
                print("Usage: controlgit create-token <fine-grained|classic> <scope1> [scope2] ...")
                return
            token_type = sys.argv[2]
            scopes = sys.argv[3:]
            controlgit.create_token(token_type, scopes)
        
        elif first_arg == "my-forks":
            controlgit.my_forks()
        
        elif first_arg == "my-pull-requests":
            controlgit.my_pull_requests()
        
        elif first_arg == "help":
            print_help()
        
        # Handle repo-name commands: controlgit repo-name command [args]
        else:
            repo_name = first_arg
            
            if len(sys.argv) < 3:
                print(f"Usage: controlgit {repo_name} <fork|info|url|issues|fork-list|config> [args]")
                return
            
            repo_command = sys.argv[2]
            
            if repo_command == "fork":
                controlgit.repo_fork(repo_name)
            
            elif repo_command == "info":
                controlgit.repo_info(repo_name)
            
            elif repo_command == "url":
                if len(sys.argv) < 4:
                    print(f"Usage: controlgit {repo_name} url <custom-url>")
                    return
                custom_url = sys.argv[3]
                controlgit.repo_set_url(repo_name, custom_url)
            
            elif repo_command == "issues":
                controlgit.repo_issues(repo_name)
            
            elif repo_command == "fork-list":
                controlgit.repo_fork_list(repo_name)
            
            elif repo_command == "config":
                category = sys.argv[3] if len(sys.argv) > 3 else None
                controlgit.repo_config(repo_name, category)
            
            else:
                print(f"Unknown command: {repo_command}")
                print(f"Available commands: fork, info, url, issues, fork-list, config")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_help():
    """Print help message"""
    print("""
ControlGit - GitHub Account and Repository Management

USAGE:
  controlgit <command> [args]
  controlgit <repo-name> <command> [args]

GLOBAL COMMANDS:
  auth set <username> <token>     Set GitHub credentials
  auth status                     Show authentication status
  auth clear                      Clear stored credentials
  
  settings [category]             Show account settings categories
  list-settings                   List all account settings
  change-setting <name> <value>   Change account setting
  
  create-token <type> <scopes>    Create GitHub token
                                  Types: fine-grained, classic
  
  my-forks                        List my forked repositories
  my-pull-requests                List my pull requests
  
  help                            Show this help message

REPOSITORY COMMANDS:
  controlgit <repo-name> fork                Fork repository
  controlgit <repo-name> info                Show repository information
  controlgit <repo-name> url <url>           Set custom repository URL
  controlgit <repo-name> issues              List repository issues
  controlgit <repo-name> fork-list           List repository forks
  controlgit <repo-name> config [category]   Show repository configuration

EXAMPLES:
  controlgit auth set myuser ghp_token123
  controlgit auth status
  controlgit list-settings
  controlgit change-setting bio "Developer"
  controlgit create-token classic repo gist user
  controlgit abucodingai/smartgit fork
  controlgit abucodingai/smartgit info
  controlgit abucodingai/smartgit url https://example.com
  controlgit abucodingai/smartgit issues
  controlgit abucodingai/smartgit config General
  controlgit my-forks
  controlgit my-pull-requests
""")


if __name__ == "__main__":
    main()
