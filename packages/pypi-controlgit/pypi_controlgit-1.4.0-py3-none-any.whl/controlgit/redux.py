"""Redux n for ControlGit command handling"""

from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Action types for ControlGit"""
    AUTH_SET = "AUTH_SET"
    AUTH_STATUS = "AUTH_STATUS"
    AUTH_CLEAR = "AUTH_CLEAR"
    LIST_SETTINGS = "LIST_SETTINGS"
    CHANGE_SETTING = "CHANGE_SETTING"
    CREATE_TOKEN = "CREATE_TOKEN"
    REPO_FORK = "REPO_FORK"
    REPO_INFO = "REPO_INFO"
    REPO_URL = "REPO_URL"
    REPO_ISSUES = "REPO_ISSUES"
    REPO_FORK_LIST = "REPO_FORK_LIST"
    REPO_CONFIG = "REPO_CONFIG"
    MY_FORKS = "MY_FORKS"
    MY_PULL_REQUESTS = "MY_PULL_REQUESTS"


@dataclass
class Action:
    """Redux action"""
    type: ActionType
    payload: Dict[str, Any] = None
    repo_name: Optional[str] = None


@dataclass
class State:
    """Redux state"""
    authenticated: bool = False
    username: Optional[str] = None
    token: Optional[str] = None
    last_command: Optional[str] = None
    last_result: Optional[str] = None
    error: Optional[str] = None


class ControlGitReducer:
    """Redux reducer for ControlGit"""
    
    def __init__(self):
        self.state = State()
        self.subscribers = []
    
    def subscribe(self, callback: Callable) -> Callable:
        """Subscribe to state changes"""
        self.subscribers.append(callback)
        return lambda: self.subscribers.remove(callback)
    
    def dispatch(self, action: Action) -> State:
        """Dispatch action and update state"""
        self.state = self._reduce(self.state, action)
        self._notify_subscribers()
        return self.state
    
    def _reduce(self, state: State, action: Action) -> State:
        """Reduce action to new state"""
        if action.type == ActionType.AUTH_SET:
            return State(
                authenticated=True,
                username=action.payload.get("username"),
                token=action.payload.get("token"),
                last_command="auth set",
                last_result="✅ Authentication configured"
            )
        
        elif action.type == ActionType.AUTH_STATUS:
            if state.authenticated:
                return State(
                    authenticated=True,
                    username=state.username,
                    token=state.token,
                    last_command="auth status",
                    last_result=f"✅ Authenticated as {state.username}"
                )
            else:
                return State(
                    authenticated=False,
                    last_command="auth status",
                    last_result="❌ Not authenticated",
                    error="Not authenticated"
                )
        
        elif action.type == ActionType.AUTH_CLEAR:
            return State(
                authenticated=False,
                last_command="auth clear",
                last_result="✅ Authentication cleared"
            )
        
        elif action.type == ActionType.LIST_SETTINGS:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command="list-settings",
                last_result="✅ Account settings retrieved"
            )
        
        elif action.type == ActionType.CHANGE_SETTING:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"change-setting {action.payload.get('name')}",
                last_result=f"✅ Setting '{action.payload.get('name')}' updated"
            )
        
        elif action.type == ActionType.CREATE_TOKEN:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"create-token {action.payload.get('type')}",
                last_result=f"✅ Token created"
            )
        
        elif action.type == ActionType.REPO_FORK:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"{action.repo_name} fork",
                last_result=f"✅ Repository {action.repo_name} forked"
            )
        
        elif action.type == ActionType.REPO_INFO:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"{action.repo_name} info",
                last_result=f"✅ Repository info retrieved"
            )
        
        elif action.type == ActionType.REPO_URL:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"{action.repo_name} url",
                last_result=f"✅ Repository URL set"
            )
        
        elif action.type == ActionType.REPO_ISSUES:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"{action.repo_name} issues",
                last_result=f"✅ Issues retrieved"
            )
        
        elif action.type == ActionType.REPO_FORK_LIST:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"{action.repo_name} fork-list",
                last_result=f"✅ Forks retrieved"
            )
        
        elif action.type == ActionType.REPO_CONFIG:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command=f"{action.repo_name} config",
                last_result=f"✅ Configuration retrieved"
            )
        
        elif action.type == ActionType.MY_FORKS:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command="my-forks",
                last_result="✅ My forks retrieved"
            )
        
        elif action.type == ActionType.MY_PULL_REQUESTS:
            return State(
                authenticated=state.authenticated,
                username=state.username,
                token=state.token,
                last_command="my-pull-requests",
                last_result="✅ My pull requests retrieved"
            )
        
        return state
    
    def _notify_subscribers(self):
        """Notify all subscribers of state change"""
        for callback in self.subscribers:
            callback(self.state)
    
    def get_state(self) -> State:
        """Get current state"""
        return self.state


class CommandParser:
    """Parse controlgit commands"""
    
    @staticmethod
    def parse(command_line: str) -> tuple[ActionType, Dict[str, Any], Optional[str]]:
        """
        Parse command line into action type, payload, and repo name
        
        Format: controlgit <command> [repo-name] [args]
        """
        parts = command_line.strip().split()
        
        if not parts or parts[0] != "controlgit":
            raise ValueError("Command must start with 'controlgit'")
        
        if len(parts) < 2:
            raise ValueError("Command required")
        
        command = parts[1]
        repo_name = None
        payload = {}
        
        # Global commands
        if command == "auth":
            if len(parts) < 3:
                raise ValueError("Auth subcommand required: set, status, clear")
            
            subcommand = parts[2]
            if subcommand == "set":
                if len(parts) < 5:
                    raise ValueError("Usage: controlgit auth set <username> <token>")
                payload = {"username": parts[3], "token": parts[4]}
                return ActionType.AUTH_SET, payload, None
            elif subcommand == "status":
                return ActionType.AUTH_STATUS, {}, None
            elif subcommand == "clear":
                return ActionType.AUTH_CLEAR, {}, None
        
        elif command == "list-settings":
            return ActionType.LIST_SETTINGS, {}, None
        
        elif command == "change-setting":
            if len(parts) < 4:
                raise ValueError("Usage: controlgit change-setting <name> <value>")
            payload = {"name": parts[2], "value": parts[3]}
            return ActionType.CHANGE_SETTING, payload, None
        
        elif command == "create-token":
            if len(parts) < 4:
                raise ValueError("Usage: controlgit create-token <type> <scope1> [scope2]...")
            payload = {"type": parts[2], "scopes": parts[3:]}
            return ActionType.CREATE_TOKEN, payload, None
        
        elif command == "my-forks":
            return ActionType.MY_FORKS, {}, None
        
        elif command == "my-pull-requests":
            return ActionType.MY_PULL_REQUESTS, {}, None
        
        # Repository commands: controlgit <repo-name> <command> [args]
        else:
            repo_name = command
            
            if len(parts) < 3:
                raise ValueError(f"Usage: controlgit {repo_name} <command> [args]")
            
            repo_command = parts[2]
            
            if repo_command == "fork":
                return ActionType.REPO_FORK, {}, repo_name
            
            elif repo_command == "info":
                return ActionType.REPO_INFO, {}, repo_name
            
            elif repo_command == "url":
                if len(parts) < 4:
                    raise ValueError(f"Usage: controlgit {repo_name} url <url>")
                payload = {"url": parts[3]}
                return ActionType.REPO_URL, payload, repo_name
            
            elif repo_command == "issues":
                return ActionType.REPO_ISSUES, {}, repo_name
            
            elif repo_command == "fork-list":
                return ActionType.REPO_FORK_LIST, {}, repo_name
            
            elif repo_command == "config":
                category = parts[3] if len(parts) > 3 else None
                payload = {"category": category}
                return ActionType.REPO_CONFIG, payload, repo_name
            
            else:
                raise ValueError(f"Unknown command: {repo_command}")
        
        raise ValueError("Invalid command")


class ControlGitStore:
    """Redux store for ControlGit"""
    
    def __init__(self, controlgit_instance):
        self.reducer = ControlGitReducer()
        self.controlgit = controlgit_instance
        self.parser = CommandParser()
    
    def execute_command(self, command_line: str) -> str:
        """Execute a controlgit command"""
        try:
            action_type, payload, repo_name = self.parser.parse(command_line)
            
            # Execute the actual command
            result = self._execute_action(action_type, payload, repo_name)
            
            # Dispatch action to update state
            action = Action(type=action_type, payload=payload, repo_name=repo_name)
            self.reducer.dispatch(action)
            
            return result
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _execute_action(self, action_type: ActionType, payload: Dict[str, Any], repo_name: Optional[str]) -> str:
        """Execute action and return result"""
        try:
            if action_type == ActionType.AUTH_SET:
                self.controlgit.auth(payload["username"], payload["token"])
                return "✅ Authentication configured"
            
            elif action_type == ActionType.AUTH_STATUS:
                self.controlgit.auth_status()
                return "✅ Status checked"
            
            elif action_type == ActionType.AUTH_CLEAR:
                self.controlgit.auth_clear()
                return "✅ Authentication cleared"
            
            elif action_type == ActionType.LIST_SETTINGS:
                self.controlgit.list_settings()
                return "✅ Settings listed"
            
            elif action_type == ActionType.CHANGE_SETTING:
                self.controlgit.change_setting(payload["name"], payload["value"])
                return f"✅ Setting '{payload['name']}' updated"
            
            elif action_type == ActionType.CREATE_TOKEN:
                self.controlgit.create_token(payload["type"], payload["scopes"])
                return "✅ Token created"
            
            elif action_type == ActionType.REPO_FORK:
                self.controlgit.repo_fork(repo_name)
                return f"✅ Repository {repo_name} forked"
            
            elif action_type == ActionType.REPO_INFO:
                self.controlgit.repo_info(repo_name)
                return f"✅ Repository info retrieved"
            
            elif action_type == ActionType.REPO_URL:
                self.controlgit.repo_set_url(repo_name, payload["url"])
                return f"✅ Repository URL set"
            
            elif action_type == ActionType.REPO_ISSUES:
                self.controlgit.repo_issues(repo_name)
                return f"✅ Issues retrieved"
            
            elif action_type == ActionType.REPO_FORK_LIST:
                self.controlgit.repo_fork_list(repo_name)
                return f"✅ Forks retrieved"
            
            elif action_type == ActionType.REPO_CONFIG:
                category = payload.get("category")
                self.controlgit.repo_config(repo_name, category)
                return f"✅ Configuration retrieved"
            
            elif action_type == ActionType.MY_FORKS:
                self.controlgit.my_forks()
                return "✅ My forks retrieved"
            
            elif action_type == ActionType.MY_PULL_REQUESTS:
                self.controlgit.my_pull_requests()
                return "✅ My pull requests retrieved"
            
            return "✅ Command executed"
        
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"
    
    def get_state(self) -> State:
        """Get current Redux state"""
        return self.reducer.get_state()
