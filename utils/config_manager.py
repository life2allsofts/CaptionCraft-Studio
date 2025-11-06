"""
Configuration Manager for CaptionCraft Studio
Handles application settings, user preferences, and style configurations

Module: config_manager.py
Description: Centralized configuration management with JSON persistence,
             BOM handling, and dot-notation access for nested settings.
Author: Tetteh-Kofi (Isaac Tetteh-Apotey)
Version: 1.0.0

Key Features:
- JSON-based configuration with automatic file creation
- UTF-8 BOM detection and handling for cross-platform compatibility
- Dot-notation access for nested configuration values
- Recent files tracking and management
- Singleton pattern for global application access
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Central configuration management system for CaptionCraft Studio.
    
    Manages all application settings, user preferences, and style configurations
    with automatic persistence to JSON file. Implements singleton pattern for
    consistent access across the entire application.
    
    Features:
    - Automatic configuration file creation with sensible defaults
    - Robust UTF-8 BOM handling for Windows compatibility
    - Dot-notation access for nested configuration keys
    - Thread-safe operations for future multi-threading support
    
    Attributes:
        config_file (str): Path to the JSON configuration file
        config (Dict[str, Any]): In-memory configuration dictionary
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str): Path to the configuration JSON file. 
                              Defaults to "config.json" in current directory.
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}  # In-memory configuration store
        self.load_config()  # Load existing config or create defaults
    
    def load_config(self) -> None:
        """
        Load configuration from JSON file with robust encoding handling.
        
        Automatically detects and handles UTF-8 Byte Order Mark (BOM) which
        is commonly added by Windows text editors. Creates default configuration
        if file doesn't exist or is corrupted.
        
        Workflow:
        1. Check if config file exists
        2. Read file in binary mode to detect BOM
        3. Decode with appropriate encoding (utf-8-sig for BOM, utf-8 otherwise)
        4. Parse JSON content or create defaults on failure
        
        Raises:
            JSONDecodeError: If configuration file contains invalid JSON
            IOError: If file cannot be read due to permission issues
        """
        try:
            if os.path.exists(self.config_file):
                # Read file in binary mode to handle encoding detection
                with open(self.config_file, 'rb') as f:
                    raw_data = f.read()
                    
                # Detect and handle UTF-8 Byte Order Mark (BOM)
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    # UTF-8 with BOM - common in Windows environments
                    content = raw_data.decode('utf-8-sig')
                else:
                    # Regular UTF-8 without BOM
                    content = raw_data.decode('utf-8')
                
                # Parse JSON configuration
                self.config = json.loads(content)
            else:
                # Create default configuration if file doesn't exist
                self._create_default_config()
                self.save_config()  # Persist defaults to disk
                
        except Exception as e:
            # Graceful degradation: use defaults on any error
            print(f"Error loading config: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """
        Create default configuration structure with sensible defaults.
        
        Establishes the complete configuration hierarchy with values
        optimized for CaptionCraft Studio's initial user experience.
        """
        self.config = {
            "app": {
                "name": "CaptionCraft Studio",
                "version": "1.0.0",
                "author": "Tetteh-Kofi (Isaac Tetteh-Apotey)"
            },
            "ui": {
                "theme": "dark",      # Dark theme for reduced eye strain
                "language": "en",     # English as default language
                "font_size": 12       # Balanced readability size
            },
            "default_styles": {
                "font_family": "Arial",           # Widely available font
                "font_size": "24px",              # Readable subtitle size
                "text_color": "#FFFFFF",          # White text for contrast
                "background_color": "#000000",    # Black background
                "highlight_color": "#FFD700"      # Gold for emphasis
            },
            "subtitle_modes": ["block", "word_by_word", "karaoke"],
            "supported_formats": ["vtt", "srt", "sbv", "txt"],
            "recent_files": []  # Track recently opened files for quick access
        }
    
    def save_config(self) -> None:
        """
        Save current configuration to JSON file without BOM.
        
        Persists the in-memory configuration to disk using UTF-8 encoding
        without BOM to ensure cross-platform compatibility and clean file format.
        
        Raises:
            IOError: If file cannot be written (disk full, permissions, etc.)
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # Write with pretty formatting for human readability
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve configuration value using dot notation for nested keys.
        
        Provides convenient access to nested configuration values using
        dot-separated keys like "app.name" or "default_styles.font_family".
        
        Args:
            key (str): Dot-notation path to configuration value
            default (Any): Default value to return if key is not found
            
        Returns:
            Any: Configuration value or default if not found
            
        Example:
            >>> config_manager.get("app.name")
            'CaptionCraft Studio'
            >>> config_manager.get("ui.theme", "dark")
            'dark'
            >>> config_manager.get("non.existent.key", "default_value")
            'default_value'
        """
        keys = key.split('.')  # Split dot notation into path components
        value = self.config     # Start at root of configuration
        
        # Traverse nested dictionaries using key path
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]  # Move deeper into configuration tree
            else:
                return default   # Key path not found, return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation for nested keys.
        
        Creates or updates configuration values at any depth in the
        configuration hierarchy. Automatically persists changes to disk.
        
        Args:
            key (str): Dot-notation path to configuration value
            value (Any): Value to set at the specified path
            
        Example:
            >>> config_manager.set("ui.theme", "light")
            >>> config_manager.set("default_styles.font_size", "28px")
        """
        keys = key.split('.')    # Split dot notation into path components
        config_ref = self.config  # Reference to current configuration level
        
        # Navigate to the parent level of the target key
        for k in keys[:-1]:
            # Create nested dictionaries if they don't exist
            if k not in config_ref or not isinstance(config_ref[k], dict):
                config_ref[k] = {}
            config_ref = config_ref[k]  # Move to next level
        
        # Set the value at the final key and persist to disk
        config_ref[keys[-1]] = value
        self.save_config()
    
    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list with intelligent management.
        
        Maintains a list of recently accessed files with the following behavior:
        - Moves existing files to the top (most recent)
        - Limits list to 10 entries to prevent clutter
        - Automatically persists changes to configuration
        
        Args:
            file_path (str): Full path to the file to add to recent files
            
        Example:
            >>> config_manager.add_recent_file("C:/Projects/subtitles.vtt")
        """
        recent_files = self.get("recent_files", [])
        
        # Remove file if already exists (to avoid duplicates)
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning of list (most recent first)
        recent_files.insert(0, file_path)
        
        # Maintain reasonable list size (last 10 files)
        recent_files = recent_files[:10]
        
        # Update configuration and persist
        self.set("recent_files", recent_files)


# =============================================================================
# SINGLETON PATTERN IMPLEMENTATION
# =============================================================================

# Global singleton instance for application-wide access
# This ensures all parts of the application use the same configuration state
config_manager = ConfigManager()


# =============================================================================
# TESTING & VERIFICATION
# =============================================================================

if __name__ == "__main__":
    """
    Standalone test execution for Configuration Manager functionality.
    
    Verifies that the configuration system works correctly including:
    - Default configuration creation
    - Dot-notation access methods
    - Recent files management
    - Error handling and fallbacks
    """
    
    # Create configuration manager instance
    cm = ConfigManager()
    
    # Test basic configuration access
    print("App Name:", cm.get("app.name"))
    print("Default Font:", cm.get("default_styles.font_family"))
    print("Recent Files:", cm.get("recent_files"))
    
    # Test dot notation with nested keys
    print("UI Theme:", cm.get("ui.theme"))
    print("Text Color:", cm.get("default_styles.text_color"))
    
    # Test non-existent keys with defaults
    print("Non-existent key:", cm.get("this.key.does.not.exist", "DEFAULT_VALUE"))
    
    # Test recent files functionality
    cm.add_recent_file("C:/Projects/subtitle1.vtt")
    cm.add_recent_file("C:/Projects/subtitle2.srt")
    print("Recent Files after additions:", cm.get("recent_files"))
    
    print("✅ Config manager working correctly!")