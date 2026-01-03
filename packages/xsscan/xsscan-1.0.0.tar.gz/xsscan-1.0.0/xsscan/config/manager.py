"""
Configuration Manager - Handles persistent configuration storage.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from appdirs import user_config_dir


class ConfigManager:
    """Manages persistent configuration storage."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = Path(user_config_dir("xsscan"))
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def save(self, config: Dict[str, Any]):
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
        """
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        config = self.load()
        return config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        config = self.load()
        
        # Type conversion for common settings
        if key in ("default_depth", "max_threads"):
            value = int(value)
        elif key in ("default_timeout", "rate_limit"):
            value = float(value)
        elif key in ("verify_ssl", "follow_redirects"):
            value = value.lower() in ("true", "1", "yes", "on")
        elif key in ("headers", "cookies", "excluded_paths", "excluded_params"):
            # These should be JSON strings
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        
        config[key] = value
        self.save(config)
    
    def reset(self):
        """Reset configuration to defaults."""
        if self.config_file.exists():
            self.config_file.unlink()

