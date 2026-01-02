#!/usr/bin/env python3

# File: sphinxcolor/extension.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT

"""
Sphinx extension for sphinxcolor
MONKEY-PATCHES ColorizeFormatter to use Rich colors instead
"""
import logging
import re
from sphinx.application import Sphinx
from sphinx.util.console import strip_colors
from rich.console import Console
from rich.text import Text
from .config import Config


class RichFormatter(logging.Formatter):
    """
    Custom formatter that colorizes ALL Sphinx WARNING/ERROR messages with Rich
    Replaces Sphinx's ColorizeFormatter
    """
    
    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config or Config()
        self.console = Console(force_terminal=True, legacy_windows=False, stderr=True)
        
        # Multiple patterns for different WARNING formats
        self.patterns = [
            re.compile(r'^(.+?\.(?:py|rst|md)):(.+?):(\d+):\s*(WARNING|ERROR):\s*(.+?)$', re.IGNORECASE),
            re.compile(r'^(.+?\.(?:py|rst|md)):(.+?):\s*(WARNING|ERROR):\s*(.+?)$', re.IGNORECASE),
            re.compile(r'^(.+?\.(?:py|rst|md)):(\d+):\s*(WARNING|ERROR):\s*(.+?)$', re.IGNORECASE),
            re.compile(r'^(.+?\.(?:py|rst|md)):\s*(WARNING|ERROR):\s*(.+?)$', re.IGNORECASE),
        ]
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with Rich colors"""
        message = record.getMessage()
        message = strip_colors(message)
        
        if record.levelname in ('WARNING', 'ERROR'):
            colored = self._colorize_warning(message, record.levelname)
            if colored:
                with self.console.capture() as capture:
                    self.console.print(colored, end='')
                return capture.get().rstrip('\n')
        
        return message
    
    def _colorize_warning(self, message: str, level: str) -> Text:
        """Try ALL patterns to colorize warning"""
        msg_stripped = message.strip()
        
        for i, pattern in enumerate(self.patterns):
            match = pattern.match(msg_stripped)
            if match:
                groups = match.groups()
                if i == 0:
                    return self._build_colored(groups[0], groups[1], groups[2], groups[3], groups[4])
                elif i == 1:
                    return self._build_colored(groups[0], groups[1], None, groups[2], groups[3])
                elif i == 2:
                    return self._build_colored(groups[0], None, groups[1], groups[2], groups[3])
                elif i == 3:
                    return self._build_colored(groups[0], None, None, groups[1], groups[2])
        
        # Fallback
        text = Text()
        if 'WARNING:' in message:
            idx = message.index('WARNING:')
            text.append(message[:idx])
            text.append('WARNING:', style=f"{self.config.get_color('warning')} bold")
            text.append(message[idx+8:])
        elif 'ERROR:' in message:
            idx = message.index('ERROR:')
            text.append(message[:idx])
            text.append('ERROR:', style=f"{self.config.get_color('error')} bold")
            text.append(message[idx+6:])
        else:
            text = Text(message, style=self.config.get_color('warning'))
        
        return text
    
    def _build_colored(self, filepath: str, location: str, line_num: str, level: str, message: str) -> Text:
        """Build colored Text object"""
        text = Text()
        
        text.append(filepath, style=self.config.get_color('filepath'))
        
        if location:
            text.append(":", style="white")
            text.append(location, style=self.config.get_color('docstring'))
        
        if line_num:
            text.append(":", style="white")
            text.append(line_num, style=self.config.get_color('docstring'))
        
        text.append(": ", style="white")
        if level.upper() == 'ERROR':
            text.append(f"{level}:", style=f"{self.config.get_color('error')} bold")
        else:
            text.append(f"{level}:", style=f"{self.config.get_color('warning')} bold")
        
        tips = None
        msg_text = message
        if 'use :no-index:' in message:
            parts = message.split('use :no-index:', 1)
            msg_text = parts[0].strip().rstrip(',')
            tips = 'use :no-index:' + parts[1]
        
        text.append(" ")
        msg_fg = self.config.get_color('message_fg')
        msg_bg = self.config.get_color('message_bg')
        text.append(msg_text, style=f"{msg_fg} on {msg_bg}")
        
        if tips:
            tips_fg = self.config.get_color('tips_fg')
            tips_bg = self.config.get_color('tips_bg')
            text.append(" " + tips, style=f"{tips_fg} on {tips_bg} bold")
        
        return text


# Global variable to store original ColorizeFormatter
_original_colorize_formatter = None


def setup(app: Sphinx):
    """
    Setup sphinxcolor extension
    
    CRITICAL: Monkey-patch ColorizeFormatter BEFORE Sphinx creates handlers!
    """
    global _original_colorize_formatter
    
    # Add config values
    app.add_config_value('sphinxcolor_config_path', None, 'env')
    app.add_config_value('sphinxcolor_enabled', True, 'env')
    
    # MONKEY-PATCH ColorizeFormatter class!
    # This must be done BEFORE Sphinx calls logging.setup()
    try:
        from sphinx.util import logging as sphinx_logging
        
        # Save original
        _original_colorize_formatter = sphinx_logging.ColorizeFormatter
        
        # Create wrapper class that returns RichFormatter
        class ColorizeFormatterWrapper:
            """Wrapper that replaces ColorizeFormatter with RichFormatter"""
            def __new__(cls):
                # Get user config (may not be ready yet, use default)
                try:
                    config_path = getattr(app.config, 'sphinxcolor_config_path', None)
                    enabled = getattr(app.config, 'sphinxcolor_enabled', True)
                except:
                    config_path = None
                    enabled = True
                
                if enabled:
                    # Return RichFormatter instead!
                    return RichFormatter(Config(config_path))
                else:
                    # Return original if disabled
                    return _original_colorize_formatter()
        
        # REPLACE ColorizeFormatter in sphinx.util.logging module!
        sphinx_logging.ColorizeFormatter = ColorizeFormatterWrapper
        
    except Exception as e:
        import sys
        print(f"sphinxcolor: Monkey-patch failed: {e}", file=sys.stderr)
    
    # Also try to update existing handlers (if any exist already)
    def update_existing_handlers(app: Sphinx, config):
        """Update any handlers that were created before monkey-patch"""
        if not app.config.sphinxcolor_enabled:
            return
        
        try:
            config_path = getattr(app.config, 'sphinxcolor_config_path', None)
            user_config = Config(config_path)
            rich_formatter = RichFormatter(config=user_config)
            
            logger = logging.getLogger('sphinx')
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    # Replace formatter if it's the original ColorizeFormatter
                    if handler.formatter and handler.formatter.__class__.__name__ == 'ColorizeFormatter':
                        handler.setFormatter(rich_formatter)
        except Exception:
            pass
    
    # Connect to config-inited to update with user config
    app.connect('config-inited', update_existing_handlers)
    
    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }