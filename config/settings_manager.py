import os
import json

class SettingsManager:
    """
    Manages local application configuration profiles using a 
    portable JSON file interface in the config directory.
    """
    def __init__(self, filename="config.json"):
        # Anchor the configuration file directly inside this folder path
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.config_dir, filename)
        
        # Standard, secure default system profiles
        self.defaults = {
            "ollama_host": "http://localhost:11434",
            "target_model": "qwen2.5-coder:3b",
            "fallback_context_cap": 4096,
            "safety_buffer_tokens": 500,
            "auto_redact_secrets": True,
            "export_audit_logs": True
        }
        self.settings = self.load_settings()

    def load_settings(self) -> dict:
        """Loads configuration variables from disk, creating defaults if missing."""
        if not os.path.exists(self.config_path):
            self.save_settings(self.defaults)
            return self.defaults.copy()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                
            # Verify and merge loaded data with defaults to protect against corrupt fields
            verified_settings = self.defaults.copy()
            for key, val in loaded_data.items():
                if key in verified_settings:
                    verified_settings[key] = val
            return verified_settings
            
        except Exception:
            # Fallback smoothly to safety defaults if file operations are blocked
            return self.defaults.copy()

    def save_settings(self, updated_profile: dict) -> bool:
        """Writes current settings configuration to the local JSON layout file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(updated_profile, f, indent=4)
            self.settings = updated_profile.copy()
            return True
        except Exception:
            return False

    def get(self, key: str):
        """Retrieves a specific configuration parameter securely."""
        return self.settings.get(key, self.defaults.get(key))
