import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet
import threading
import time

DEFAULT_TOTP_SECRET = "BASE32SECRET3232"

class DomainConfig:
    def __init__(self, name, secret, session_duration=86400, theme="dark"):
        self.name = name
        self.totp_secret = secret
        self.session_duration = session_duration
        self.theme = theme

    def to_dict(self, fernet=None):
        secret_to_store = self.totp_secret
        if fernet:
            secret_to_store = fernet.encrypt(self.totp_secret.encode()).decode()
        
        return {
            "totp_secret": secret_to_store,
            "session_duration": self.session_duration,
            "theme": self.theme
        }

    @classmethod
    def from_dict(cls, name, data, fernet=None):
        raw_secret = data.get("totp_secret")
        if fernet and raw_secret:
            try:
                raw_secret = fernet.decrypt(raw_secret.encode()).decode()
            except Exception:
                # Fallback to raw if decryption fails (e.g. first run after migration or wrong key)
                pass
                
        return cls(
            name,
            raw_secret,
            data.get("session_duration", 86400),
            data.get("theme", "dark")
        )

class Config:
    def __init__(self):
        # Resolve config path: 1. Env Var, 2. Local File, 3. Global Fallback
        env_path = os.environ.get("OTPDOOR_CONFIG_FILE")
        local_path = "otpdoor_config.json"
        global_path = os.path.expanduser("~/.otpdoor/config.json")
        
        if env_path:
            self.config_path_file = env_path
        elif os.path.exists(local_path):
            self.config_path_file = local_path
        else:
            self.config_path_file = global_path
            
        self.cookie_encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.cookie_encryption_key)
        
        # Load core settings from env
        self.cookie_secret = os.environ.get("OTPDOOR_COOKIE_SECRET", "super-secret-key-change-me")
        self.config_fernet = self._get_config_fernet()
        
        self.cookie_name_prefix = os.environ.get("OTPDOOR_COOKIE_NAME", "OTPDOOR_AUTH")
        self.auth_path = os.environ.get("OTPDOOR_AUTH_PATH", "/_auth")
        self.check_path = os.environ.get("OTPDOOR_CHECK_PATH", "/_check")
        self.config_path = os.environ.get("OTPDOOR_CONFIG_PATH", "/_config")
        self.enable_config = False
        
        self.allowed_domains = os.environ.get("OTPDOOR_ALLOWED_DOMAINS", "").split(",")
        self.cookie_domain = os.environ.get("OTPDOOR_COOKIE_DOMAIN", None)
        self.cookie_secure = os.environ.get("OTPDOOR_COOKIE_SECURE", "false").lower() == "true"
        self.cookie_httponly = os.environ.get("OTPDOOR_COOKIE_HTTPONLY", "true").lower() == "true"
        self.cookie_samesite = os.environ.get("OTPDOOR_COOKIE_SAMESITE", "Lax")

        self.domains = {}
        self._last_mtime = 0
        self.load()

    def _get_config_fernet(self):
        # Derive a stable 32-byte key from the cookie_secret
        key_material = hashlib.sha256(self.cookie_secret.encode()).digest()
        encoded_key = base64.urlsafe_b64encode(key_material)
        return Fernet(encoded_key)

    def remove_domain(self, name):
        new_secret = None
        if name == "default":
            # Don't delete, just reset to environment/defaults
            new_secret = os.environ.get("OTPDOOR_TOTP_SECRET", DEFAULT_TOTP_SECRET)
            default_duration = int(os.environ.get("OTPDOOR_SESSION_DURATION", 86400))
            default_theme = os.environ.get("OTPDOOR_THEME", "dark")
            self.domains["default"] = DomainConfig("default", new_secret, default_duration, default_theme)
        elif name in self.domains:
            del self.domains[name]
        return new_secret

    def get_domain(self, name):
        return self.domains.get(name or "default", self.domains.get("default"))

    def load(self):
        if os.path.exists(self.config_path_file):
            try:
                with open(self.config_path_file, 'r') as f:
                    data = json.load(f)
                    # Clear current domains to stay in sync with the file (removals)
                    self.domains.clear()
                    for name, d_data in data.items():
                        self.domains[name] = DomainConfig.from_dict(name, d_data, self.config_fernet)
                print(f"[LOAD] Successfully loaded {len(self.domains)} domains from {os.path.abspath(self.config_path_file)}")
            except Exception as e:
                print(f"[LOAD ERROR] Failed to read {os.path.abspath(self.config_path_file)}: {e}")
        
        # Always ensure 'default' exists even if file is missing or domain was removed
        if "default" not in self.domains:
            default_secret = os.environ.get("OTPDOOR_TOTP_SECRET", DEFAULT_TOTP_SECRET)
            default_duration = int(os.environ.get("OTPDOOR_SESSION_DURATION", 86400))
            default_theme = os.environ.get("OTPDOOR_THEME", "dark")
            self.domains["default"] = DomainConfig("default", default_secret, default_duration, default_theme)
            print(f"[INFO] Initialized missing 'default' domain with secret: {self.domains['default'].totp_secret}")
        
        if os.path.exists(self.config_path_file):
            self._last_mtime = os.path.getmtime(self.config_path_file)
        
        print(f"[STATE] Active domains: {list(self.domains.keys())}")

    def save(self):
        try:
            # Ensure global directory exists if path is in home dir
            dir_path = os.path.dirname(self.config_path_file)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                
            data = {name: d.to_dict(self.config_fernet) for name, d in self.domains.items()}
            with open(self.config_path_file, 'w') as f:
                json.dump(data, f, indent=4)
            self._last_mtime = os.path.getmtime(self.config_path_file)
        except Exception as e:
            print(f"Error saving config: {e}")

    def export_config(self, path):
        try:
            # Export raw data (unencrypted secrets) for portability
            data = {name: d.to_dict() for name, d in self.domains.items()}
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def import_config(self, path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                for name, d_data in data.items():
                    # Import raw data (treating as unencrypted)
                    self.domains[name] = DomainConfig.from_dict(name, d_data, fernet=None)
            self.save()
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False

    def start_watcher(self):
        def _watcher_loop():
            while True:
                time.sleep(2)
                if os.path.exists(self.config_path_file):
                    mtime = os.path.getmtime(self.config_path_file)
                    if mtime > self._last_mtime:
                        print(f"\n[AUTO-RELOAD] Configuration file change detected. Reloading...")
                        self.load()
        
        thread = threading.Thread(target=_watcher_loop, daemon=True)
        thread.start()

config = Config()
