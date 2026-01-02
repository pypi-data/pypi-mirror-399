import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet

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
        self.config_path_file = os.environ.get("OPTDOOR_CONFIG_FILE", "optdoor_config.json")
        self.cookie_encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.cookie_encryption_key)
        
        # Load core settings from env
        self.cookie_secret = os.environ.get("OPTDOOR_COOKIE_SECRET", "super-secret-key-change-me")
        self.config_fernet = self._get_config_fernet()
        
        self.cookie_name_prefix = os.environ.get("OPTDOOR_COOKIE_NAME", "OPTDOOR_AUTH")
        self.auth_path = os.environ.get("OPTDOOR_AUTH_PATH", "/_auth")
        self.check_path = os.environ.get("OPTDOOR_CHECK_PATH", "/_check")
        self.config_path = os.environ.get("OPTDOOR_CONFIG_PATH", "/_config")
        self.enable_config = False
        
        self.allowed_domains = os.environ.get("OPTDOOR_ALLOWED_DOMAINS", "").split(",")
        self.cookie_domain = os.environ.get("OPTDOOR_COOKIE_DOMAIN", None)
        self.cookie_secure = os.environ.get("OPTDOOR_COOKIE_SECURE", "true").lower() == "true"
        self.cookie_httponly = os.environ.get("OPTDOOR_COOKIE_HTTPONLY", "true").lower() == "true"
        self.cookie_samesite = os.environ.get("OPTDOOR_COOKIE_SAMESITE", "Lax")

        self.domains = {}
        self.load()

        # Ensure default domain exists
        if "default" not in self.domains:
            default_secret = os.environ.get("OPTDOOR_TOTP_SECRET", DEFAULT_TOTP_SECRET)
            default_duration = int(os.environ.get("OPTDOOR_SESSION_DURATION", 86400))
            default_theme = os.environ.get("OPTDOOR_THEME", "dark")
            self.domains["default"] = DomainConfig("default", default_secret, default_duration, default_theme)
            self.save()

    def _get_config_fernet(self):
        # Derive a stable 32-byte key from the cookie_secret
        key_material = hashlib.sha256(self.cookie_secret.encode()).digest()
        encoded_key = base64.urlsafe_b64encode(key_material)
        return Fernet(encoded_key)

    def get_domain(self, name):
        return self.domains.get(name or "default", self.domains.get("default"))

    def load(self):
        if os.path.exists(self.config_path_file):
            try:
                with open(self.config_path_file, 'r') as f:
                    data = json.load(f)
                    for name, d_data in data.items():
                        self.domains[name] = DomainConfig.from_dict(name, d_data, self.config_fernet)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        try:
            data = {name: d.to_dict(self.config_fernet) for name, d in self.domains.items()}
            with open(self.config_path_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

config = Config()
