import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import getpass
from urllib.parse import urlparse, urlunparse
import threading
try:
    import keyring  # type: ignore
    KEYRING_AVAILABLE = True
except ImportError:
    keyring = None  # type: ignore
    KEYRING_AVAILABLE = False
except Exception:
    keyring = None  # type: ignore
    KEYRING_AVAILABLE = False
class AuthManager:
    def __init__(self, api_base_url: str | None = None):
        # Environment-based URL with a special 'DEV' shortcut
        is_dev = os.getenv('SAGEBOW_DEV', '').lower() in ('1', 'true', 'yes')
        default_prod = 'https://sagebow.com'
        
        if is_dev and not api_base_url:
            base = 'http://localhost:3000'
        else:
            base = api_base_url or os.getenv('SAGEBOW_API_URL') or os.getenv('EPICAI_API_URL', default_prod)
        
        try:
            parsed = urlparse(str(base))
            host = (parsed.hostname or '').lower()
            if parsed.scheme == 'http' and host not in {'localhost', '127.0.0.1'}:
                parsed = parsed._replace(scheme='https')
                base = urlunparse(parsed)
        except Exception:
            pass
        self.api_base_url = str(base).rstrip('/')
        self.config_dir = Path.home() / ".sagebow"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self._svc = "SageBow"
        self._acct = "access_token"
        self._keyring_available = KEYRING_AVAILABLE and keyring is not None
        self._keyring_warned = False
        self._session_token: Optional[str] = None
        self._session_user: Optional[Dict[str, Any]] = None

    def _ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
        try:
            os.chmod(self.config_dir, 0o700)
        except Exception:
            pass
    def _load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    def _save_config(self, config: Dict[str, Any]):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            try:
                os.chmod(self.config_file, 0o600)
            except Exception:
                pass
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    def _keyring_call(self, action: str, func, *args, timeout: float = 2.0):
        """Run keyring operations in a worker to avoid UI hangs."""
        if not KEYRING_AVAILABLE or not keyring or not self._keyring_available:
            return None, False
        result: Dict[str, Any] = {}
        def _worker():
            try:
                result['value'] = func(*args)
            except Exception as exc:  # pragma: no cover - defensive
                result['error'] = exc
        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(timeout)
        if t.is_alive() or 'error' in result:
            self._keyring_available = False
            if not self._keyring_warned:
                reason = 'timed out' if t.is_alive() else f"failed: {result.get('error')}"
                print(f"Warning: system keyring {action} {reason}. Disabling keyring for this session.")
                self._keyring_warned = True
            return None, False
        return result.get('value'), True
    def get_stored_token(self) -> Optional[str]:
        # Priority 1: In-memory session token
        if self._session_token:
            return self._session_token
            
        # Priority 2: System keyring
        if KEYRING_AVAILABLE and keyring is not None and self._keyring_available:
            token, _ = self._keyring_call('read', keyring.get_password, self._svc, self._acct)
            if token:
                self._session_token = token
                return token
                
        # Priority 3: Config file
        config = self._load_config()
        token = config.get('access_token')
        if token:
            self._session_token = token
        return token
    def store_token(self, token: str, user_info: Dict[str, Any] = None):
        """Persist token securely when possible.
        Preference order:
        1) keyring (system credential store)
        2) If SAGEBOW_ALLOW_PLAINTEXT=1, store in ~/.sagebow/config.json (chmod 600)
        3) Otherwise, do NOT persist; keep only for current session.
        """
        self._session_token = token
        if user_info:
            self._session_user = user_info
            
        persisted = False
        if KEYRING_AVAILABLE and keyring is not None and self._keyring_available:
            _, ok = self._keyring_call('write', keyring.set_password, self._svc, self._acct, token)
            persisted = ok
        if not persisted:
            allow_plain = (os.getenv('SAGEBOW_ALLOW_PLAINTEXT', '').strip() == '1') or (os.getenv('EPICAI_ALLOW_PLAINTEXT', '').strip() == '1')
            if allow_plain:
                config = self._load_config()
                config['access_token'] = token
                if user_info:
                    config['user'] = user_info
                self._save_config(config)
                persisted = True
            else:
                if not self._keyring_warned:
                    print("Warning: Could not access system keyring. Token will not be stored persistently for future sessions. Using in-memory storage for now. Set SAGEBOW_ALLOW_PLAINTEXT=1 to allow plaintext storage (chmod 600).")
                    self._keyring_warned = True
        if persisted and user_info:
            config = self._load_config()
            config['user'] = user_info
            self._save_config(config)
    def clear_token(self):
        self._session_token = None
        self._session_user = None
        if KEYRING_AVAILABLE and keyring is not None and self._keyring_available:
            self._keyring_call('delete', keyring.delete_password, self._svc, self._acct)
        config = self._load_config()
        removed = False
        if 'access_token' in config:
            config.pop('access_token', None)
            removed = True
        if 'user' in config:
            config.pop('user', None)
            removed = True
        if removed:
            self._save_config(config)
    def validate_token(self, token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        try:
            response = requests.post(
                f"{self.api_base_url}/api/tokens/validate",
                json={"token": token},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "sagebow-client/0.1",
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('valid') or data.get('user'):
                    return True, data
            elif response.status_code == 403:
                data = response.json()
                error_msg = data.get('error')
                if error_msg:
                    print(f"\n❌ {error_msg}")
                return False, None
            return False, None
        except requests.exceptions.RequestException:
            return False, None
    def prompt_for_token(self) -> Optional[str]:
        print("\n" + "="*60)
        print("🔐 AUTHENTICATION REQUIRED")
        print("="*60)
        print("To use SageBow, you need an access token from your dashboard.")
        print(f"1. Visit: {self.api_base_url}/login")
        print("2. Sign up or log in to your account")
        print("3. Go to your dashboard and copy your access token")
        print("4. Paste it below")
        print("-"*60)
        token = getpass.getpass("Enter your access token: ").strip()
        return token if token else None
    def authenticate(self) -> bool:
        stored_token = self.get_stored_token()
        if stored_token:
            print()
            print("🔍 Validating stored token...")
            is_valid, user_data = self.validate_token(stored_token)
            if is_valid:
                print(f"✅ Welcome back, {user_data.get('user', {}).get('email', 'User')}!")
                return True
            else:
                print("❌ Stored token is invalid or expired.")
                self.clear_token()
        while True:
            token = self.prompt_for_token()
            if not token:
                print("❌ Authentication cancelled.")
                return False
            print("🔍 Validating token...")
            is_valid, user_data = self.validate_token(token)
            if is_valid:
                self.store_token(token, user_data)
                print(f"✅ Authentication successful! Welcome, {user_data.get('user', {}).get('email', 'User')}!")
                return True
            else:
                print("❌ Invalid token. Please check your token and try again.")
                retry = input("Try again? (y/n): ").lower().strip()
                if retry != 'y':
                    print("❌ Authentication cancelled.")
                    return False
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        config = self._load_config()
        return config.get('user')
_auth_manager = None
def get_auth_manager() -> AuthManager:
    global _auth_manager
    if _auth_manager is None:
        # We don't pass a default here anymore, 
        # let AuthManager.__init__ handle the SAGEBOW_DEV logic
        api_url = os.getenv('SAGEBOW_API_URL') or os.getenv('EPICAI_API_URL')
        _auth_manager = AuthManager(api_url)
    return _auth_manager
def require_authentication() -> bool:
    auth_manager = get_auth_manager()
    return auth_manager.authenticate()
def get_current_user() -> Optional[Dict[str, Any]]:
    auth_manager = get_auth_manager()
    return auth_manager.get_user_info()
def logout():
    auth_manager = get_auth_manager()
    auth_manager.clear_token()
    print("✅ Logged out successfully.")
