#!/usr/bin/env python3

# File: sphinxcolor/__main__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT

"""
Command-line interface for sphinxcolor
Allows using sphinxcolor as a pipe or standalone tool
"""
import sys
import argparse
try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawDescriptionHelpFormatter
from .config import Config
from .colorizer import SphinxColorizer


def main():
    """Main entry point for sphinxcolor CLI"""
    parser = argparse.ArgumentParser(
        description="Colorize Sphinx build output",
        formatter_class=CustomRichHelpFormatter,
        epilog="""
Examples:
  # Use as pipe
  sphinx-build -b html source build | sphinxcolor
  make html | sphinxcolor
  
  # Process file
  sphinxcolor < build.log
  sphinxcolor build.log
  
  # Custom config
  sphinxcolor --config custom.toml < build.log
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Input file to colorize (default: stdin)'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to sphinxcolor.toml config file'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colors (pass through)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='sphinxcolor 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Handle no-color mode
    if args.no_color:
        if args.file:
            with open(args.file, 'r') as f:
                for line in f:
                    print(line, end='')
        else:
            for line in sys.stdin:
                print(line, end='')
        return
    
    # Load configuration
    config = Config(args.config)
    colorizer = SphinxColorizer(config)
    
    # Process input
    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                colorizer.process_stream(f)
        else:
            colorizer.process_stream(sys.stdin)
    except KeyboardInterrupt:
        sys.exit(0)
    except BrokenPipeError:
        # Handle broken pipe gracefully (e.g., when piping to head)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()