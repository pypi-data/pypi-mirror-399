import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from ruamel.yaml import YAML
from iceberg_cli.utils import print_error, print_info

class ProfileManager:
    def __init__(self):
        self.config_path = Path.home() / ".pyiceberg.yaml"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.exists():
            # Create empty structure in block style
            # Create empty structure in block style (avoiding {} flow style)
            with open(self.config_path, "w") as f:
                f.write("catalog:\n  # managed by iceberg-cli\n")

    def get_config(self) -> Dict[str, Any]:
        """Reads the full configuration."""
        if not self.config_path.exists():
            return {"catalog": {}}
        try:
            with open(self.config_path, "r") as f:
                return self.yaml.load(f) or {"catalog": {}}
        except Exception as e:
            print_error(f"Failed to load config: {e}")
            return {"catalog": {}}

    def save_config(self, config: Dict[str, Any]):
        """Saves the configuration."""
        with open(self.config_path, "w") as f:
            self.yaml.dump(config, f)

    def list_profiles(self) -> Dict[str, Any]:
        """Returns the dictionary of defined catalogs."""
        config = self.get_config()
        return config.get("catalog", {})

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        profiles = self.list_profiles()
        return profiles.get(name)

    def add_profile(self, name: str, uri: str, extra_config: Dict[str, str] = None) -> bool:
        """Adds or updates a profile."""
        config = self.get_config()
        config = self.get_config()
        if "catalog" not in config or config["catalog"] is None:
            config["catalog"] = {}
        
        # Base config for a REST catalog (assuming default, can be overridden)
        profile_config = {
            "uri": uri,
        }
        
        # Default type to rest if not specified, though pyiceberg infers it often.
        # We'll just set what's given. 
        if extra_config:
            profile_config.update(extra_config)
            
        config["catalog"][name] = profile_config
        
        try:
            self.save_config(config)
            return True
        except Exception as e:
            print_error(f"Failed to save profile: {e}")
            return False

            print_error(f"Failed to save profile: {e}")
            return False

    def update_profile(self, name: str, uri: str = None, extra_config: Dict[str, str] = None) -> bool:
        """Updates an existing profile with new values (partial update)."""
        config = self.get_config()
        if "catalog" not in config or name not in config["catalog"]:
            return False

        profile = config["catalog"][name]
        
        if uri:
            profile["uri"] = uri
            
        if extra_config:
            profile.update(extra_config)
            
        # Remove keys if needed? 
        # The user request "change any value" usually implies setting/overwriting.
        # Removing keys might need a separate flag or special value (e.g. None), 
        # but for now we focus on setting/updating.
            
        try:
            self.save_config(config)
            return True
        except Exception as e:
            print_error(f"Failed to save profile: {e}")
            return False

    def remove_profile(self, name: str) -> bool:
        config = self.get_config()
        if "catalog" in config and name in config["catalog"]:
            del config["catalog"][name]
            self.save_config(config)
            return True
        return False
        config = self.get_config()
        if "catalog" in config and name in config["catalog"]:
            del config["catalog"][name]
            self.save_config(config)
            return True
        return False

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Renames a profile key."""
        config = self.get_config()
        if "catalog" not in config:
            return False
            
        catalogs = config["catalog"]
        if old_name not in catalogs:
            return False
            
        if new_name in catalogs:
            # Prevent overwriting existing profile by rename to avoid data loss confusion
            return False
            
        # Move config
        catalogs[new_name] = catalogs.pop(old_name)
        
        try:
            self.save_config(config)
            return True
        except Exception as e:
            print_error(f"Failed to rename profile: {e}")
            return False
