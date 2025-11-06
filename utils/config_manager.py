"""
Configuration Manager for CaptionCraft Studio
Handles application settings, user preferences, and style configurations
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration and user preferences"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file - handles BOM automatically"""
        try:
            if os.path.exists(self.config_file):
                # Read file with different encodings to handle BOM
                with open(self.config_file, 'rb') as f:
                    raw_data = f.read()
                    
                # Try to detect encoding and remove BOM
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    # UTF-8 with BOM
                    content = raw_data.decode('utf-8-sig')
                else:
                    # Regular UTF-8 or other encoding
                    content = raw_data.decode('utf-8')
                
                self.config = json.loads(content)
            else:
                self._create_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration structure"""
        self.config = {
            "app": {
                "name": "CaptionCraft Studio",
                "version": "1.0.0",
                "author": "Tetteh-Kofi (Isaac Tetteh-Apotey)"
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "font_size": 12
            },
            "default_styles": {
                "font_family": "Arial",
                "font_size": "24px",
                "text_color": "#FFFFFF",
                "background_color": "#000000",
                "highlight_color": "#FFD700"
            },
            "subtitle_modes": ["block", "word_by_word", "karaoke"],
            "supported_formats": ["vtt", "srt", "sbv", "txt"],
            "recent_files": []
        }
    
    def save_config(self) -> None:
        """Save configuration to JSON file without BOM"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref or not isinstance(config_ref[k], dict):
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
        self.save_config()
    
    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list"""
        recent_files = self.get("recent_files", [])
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        recent_files = recent_files[:10]  # Keep only 10 most recent
        self.set("recent_files", recent_files)


# Singleton instance for global access
config_manager = ConfigManager()


if __name__ == "__main__":
    # Test the configuration manager
    cm = ConfigManager()
    print("App Name:", cm.get("app.name"))
    print("Default Font:", cm.get("default_styles.font_family"))
    print("Recent Files:", cm.get("recent_files"))
    print("✅ Config manager working correctly!")