#!/usr/bin/env python3
"""
Legion Configuration Management
Handles settings persistence for Legion Power Manager
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration operation fails"""
    pass


class LegionConfig:
    """
    Configuration manager for Legion Power Manager
    
    Handles:
    - User settings persistence
    - Default values
    - Config file management
    """
    
    # Configuration paths
    CONFIG_DIR = Path.home() / ".config" / "legion-power"
    CONFIG_FILE = CONFIG_DIR / "settings.json"
    STATE_FILE = CONFIG_DIR / "state.json"
    
    # Default configuration
    DEFAULT_CONFIG = {
        # Display settings
        'show_percentage': True,
        'show_time_remaining': True,
        'show_notifications': True,
        
        # Auto-switching
        'auto_switch_ac_battery': True,
        'ac_power_profile': 'performance',
        'battery_power_profile': 'balanced',
        'ac_fan_mode': 'auto',
        'battery_fan_mode': 'quiet',
        
        # Conservation mode
        'conservation_mode_enabled': False,
        
        # Rapid charge
        'rapid_charge_enabled': False,
        
        # Fan mode
        'fan_mode': 'auto',
        
        # Power profile
        'power_profile': 'balanced',
        
        # Advanced
        'restore_on_boot': True,
        'start_minimized': False,
        'check_updates': True,
        
        # GUI settings
        'window_width': 800,
        'window_height': 600,
        'last_tab': 'battery',
    }
    
    def __init__(self):
        """Initialize configuration manager"""
        self._ensure_config_dir()
        self._config = self._load_config()
        self._state = self._load_state()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        try:
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Config directory: {self.CONFIG_DIR}")
        except Exception as e:
            raise ConfigError(f"Failed to create config directory: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.CONFIG_FILE.exists():
            logger.info("Config file not found, using defaults")
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                user_config = json.load(f)
            
            # Merge with defaults (in case new keys were added)
            config = self.DEFAULT_CONFIG.copy()
            config.update(user_config)
            
            logger.info(f"Loaded configuration from {self.CONFIG_FILE}")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            logger.info("Using default configuration")
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self.DEFAULT_CONFIG.copy()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load runtime state from file"""
        if not self.STATE_FILE.exists():
            return {}
        
        try:
            with open(self.STATE_FILE, 'r') as f:
                state = json.load(f)
            logger.debug("Loaded state file")
            return state
        except Exception as e:
            logger.debug(f"Failed to load state: {e}")
            return {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Saved configuration to {self.CONFIG_FILE}")
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")
    
    def save_state(self):
        """Save runtime state to file"""
        try:
            with open(self.STATE_FILE, 'w') as f:
                json.dump(self._state, f, indent=2)
            logger.debug("Saved state file")
        except Exception as e:
            logger.warning(f"Failed to save state: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Value to set
            save: Whether to save immediately
        """
        self._config[key] = value
        logger.debug(f"Set config: {key} = {value}")
        
        if save:
            self.save_config()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get runtime state value"""
        return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any, save: bool = True):
        """Set runtime state value"""
        self._state[key] = value
        
        if save:
            self.save_state()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        logger.info("Configuration reset to defaults")
    
    def export_config(self, path: Path):
        """Export configuration to a file"""
        try:
            with open(path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Exported configuration to {path}")
        except Exception as e:
            raise ConfigError(f"Failed to export config: {e}")
    
    def import_config(self, path: Path):
        """Import configuration from a file"""
        try:
            with open(path, 'r') as f:
                imported = json.load(f)
            
            # Validate imported config
            config = self.DEFAULT_CONFIG.copy()
            config.update(imported)
            
            self._config = config
            self.save_config()
            logger.info(f"Imported configuration from {path}")
        except Exception as e:
            raise ConfigError(f"Failed to import config: {e}")


if __name__ == "__main__":
    # Test configuration manager
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        config = LegionConfig()
        print("✅ Configuration manager initialized\n")
        
        print("📋 Current configuration:")
        for key, value in config.get_all().items():
            print(f"  {key}: {value}")
        
        print(f"\n📁 Config file: {config.CONFIG_FILE}")
        print(f"📁 Config dir: {config.CONFIG_DIR}")
        
    except ConfigError as e:
        print(f"❌ Config Error: {e}")
        exit(1)
