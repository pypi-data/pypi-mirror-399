#!/usr/bin/env python3

# File: sphinxcolor/config.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT

"""
Configuration loader for sphinxcolor
Loads color schemes from sphinxcolor.toml
"""
import os
from pathlib import Path
from typing import Dict, Any

try:
    import tomli as tomllib
except ImportError:
    try:
        import tomllib
    except ImportError:
        import toml as tomllib


DEFAULT_CONFIG = {
    "colors": {
        "filepath": "#00FFFF",  # Cyan
        "warning": "red on #FFFF00",  # Yellow
        "line_number_fg": "#FFFFFF",  # White
        "line_number_bg": "#0000FF",  # Blue
        "docstring": "#FFAA00",  # Purple
        "message_fg": "#000000",  # Black
        # "message_fg": "#00FF00",  # Black
        "message_bg": "#00FF00",  # Green
        # "message_bg": "#000000",  # Green
        "tips_fg": "#FFFFFF",  # White
        "tips_bg": "#5500FF",  # Purple
        "error": "#FF0000",  # Red
        "info": "#00FF00",  # Green
    },
    "patterns": {
        "filepath_pattern": r"^([A-Z]:\\[^:]+|/[^:]+)",
        "warning_pattern": r"\b(WARNING|Error|ERROR)\s*:",
        "line_number_pattern": r":(\d+):",
        "tips_pattern": r"use :no-index: for one of them",
    }
}


class Config:
    """Configuration manager for sphinxcolor"""
    
    def __init__(self, config_path: str = None):
        self.config = DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load_config(config_path)
        else:
            # Try to find sphinxcolor.toml in current dir or parent dirs
            self.auto_load_config()
    
    def auto_load_config(self):
        """Try to find and load sphinxcolor.toml automatically"""
        search_paths = [
            Path.cwd() / "sphinxcolor.toml",
            Path.cwd() / ".sphinxcolor.toml",
            Path.home() / ".config" / "sphinxcolor" / "sphinxcolor.toml",
            Path.home() / ".sphinxcolor.toml",
        ]
        
        for path in search_paths:
            if path.exists():
                self.load_config(str(path))
                break
    
    def load_config(self, config_path: str):
        """Load configuration from TOML file"""
        try:
            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)
            
            # Merge user config with defaults
            if "colors" in user_config:
                self.config["colors"].update(user_config["colors"])
            if "patterns" in user_config:
                self.config["patterns"].update(user_config["patterns"])
                
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
    
    def get_color(self, key: str) -> str:
        """Get color value by key"""
        return self.config["colors"].get(key, "#FFFFFF")
    
    def get_pattern(self, key: str) -> str:
        """Get regex pattern by key"""
        return self.config["patterns"].get(key, "")
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all color settings"""
        return self.config["colors"]
    
    def get_all_patterns(self) -> Dict[str, str]:
        """Get all pattern settings"""
        return self.config["patterns"]