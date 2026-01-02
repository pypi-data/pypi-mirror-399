#!/usr/bin/env python3

# File: sphinxcolor/colorizer.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT

"""
Core colorization logic for sphinxcolor
Uses rich library to apply colors to sphinx-build output
"""
import re
from typing import Optional
from rich.console import Console
from rich.text import Text
from .config import Config


class SphinxColorizer:
    """Colorize sphinx-build output based on patterns"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.console = Console(force_terminal=True)
        
        # Pattern for WARNING/ERROR lines
        # Format 1: C:\path\file.py:docstring...:NUM: WARNING: message use :no-index:...
        # Format 2: C:\path\file.rst:NUM: WARNING: message
        self.warning_pattern = re.compile(
            r'^(.+?\.(py|rst|md)):(.+?):\s*(WARNING|ERROR):\s*(.+?)$',
            re.IGNORECASE
        )
    
    def colorize_line(self, line: str) -> Text:
        """
        Colorize a single line of sphinx output
        
        Returns:
            Rich Text object with applied colors
        """
        # Strip line untuk matching
        line_stripped = line.strip()
        
        # Try match WARNING/ERROR pattern
        match = self.warning_pattern.match(line_stripped)
        if match:
            filepath = match.group(1)  # e.g., C:\...\keys.py
            # group(2) is extension (.py, .rst, etc) - skip
            location = match.group(3)  # e.g., docstring of...:1 or just line number
            level = match.group(4)     # WARNING or ERROR
            message = match.group(5)   # rest of message
            
            # Check if message contains tips
            tips = None
            if 'use :no-index:' in message:
                parts = message.split('use :no-index:', 1)
                message = parts[0].strip().rstrip(',')
                tips = 'use :no-index:' + parts[1]
            
            return self._build_colored_warning(filepath, location, level, message, tips)
        
        # Special formatting for other lines
        if line_stripped.startswith('Running Sphinx'):
            return Text(line, style="bold #00FFFF")
        elif line_stripped.startswith('building ['):
            return Text(line, style="cyan")
        elif line_stripped.startswith('reading sources'):
            return Text(line, style="blue")
        elif line_stripped.startswith('writing output'):
            return Text(line, style="blue")
        elif 'build succeeded' in line_stripped.lower():
            return Text(line, style="bold green")
        elif line_stripped == 'done':
            return Text(line, style="green")
        elif line_stripped.startswith('['):
            return Text(line, style="yellow")
        
        # Default: no special coloring
        return Text(line)
    
    def _build_colored_warning(self, filepath: str, location: str, level: str, message: str, tips: Optional[str]) -> Text:
        """Build colored Text object for warning/error line"""
        text = Text()
        
        # Filepath - Cyan
        text.append(filepath, style=self.config.get_color('filepath'))
        
        # Separator and location - Purple
        text.append(":", style="white")
        text.append(location, style=self.config.get_color('docstring'))
        
        # Level (WARNING/ERROR) - Yellow or Red, BOLD
        text.append(": ", style="white")
        if level.upper() == 'ERROR':
            text.append(f"{level}:", style=f"{self.config.get_color('error')} bold")
        else:
            text.append(f"{level}:", style=f"black on {self.config.get_color('warning')}")
        
        # Message - Black on Green background
        text.append(" ", style="default")
        msg_fg = self.config.get_color('message_fg')
        msg_bg = self.config.get_color('message_bg')
        text.append(message, style=f"{msg_fg} on {msg_bg}")
        
        # Tips if present - White on Purple, BOLD
        if tips:
            tips_fg = self.config.get_color('tips_fg')
            tips_bg = self.config.get_color('tips_bg')
            text.append(" " + tips, style=f"{tips_fg} on {tips_bg} bold")
        
        return text
    
    def process_stream(self, stream):
        """Process input stream line by line and colorize output"""
        try:
            for line in stream:
                line = line.rstrip('\n\r')
                colored = self.colorize_line(line)
                self.console.print(colored)
        except KeyboardInterrupt:
            pass
        except BrokenPipeError:
            pass


def colorize_line(line: str, config: Optional[Config] = None) -> Text:
    """
    Standalone function to colorize a single line
    
    Args:
        line: Line to colorize
        config: Optional Config object
        
    Returns:
        Rich Text object with colors applied
    """
    colorizer = SphinxColorizer(config)
    return colorizer.colorize_line(line)