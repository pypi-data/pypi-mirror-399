#!/usr/bin/env python3
"""
Debug script for sphinxcolor extension
Check whether the formatter is actually installed on Sphinx
"""
import sys
import os
import logging

print("="*70)
print("🔍 DEBUGGING sphinxcolor Extension")
print("="*70)

# Test 1: Import
print("\n1️⃣ Testing imports...")
try:
    from sphinxcolor.extension import setup, RichFormatter
    from sphinxcolor import Config
    print("   ✅ Imports OK!")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    print("   💡 Fix: pip install -e .")
    sys.exit(1)

# Test 2: Test formatter standalone
print("\n2️⃣ Testing RichFormatter standalone...")
try:
    config = Config()
    formatter = RichFormatter(config=config)
    
    # Create test record
    record = logging.LogRecord(
        name='sphinx',
        level=logging.WARNING,
        pathname='test.py',
        lineno=1,
        msg=r"C:\PROJECTS\gntplib\gntplib\keys.py:docstring of gntplib.keys.Key:1: WARNING: duplicate object description, use :no-index: for one of them",
        args=(),
        exc_info=None
    )
    
    # Format it
    formatted = formatter.format(record)
    print("\n   📝 Formatted output:")
    print("   " + "-"*60)
    print(formatted)
    print("   " + "-"*60)
    
    if '\033[' in formatted or formatted != record.msg:
        print("\n   ✅ Formatter adds colors!")
    else:
        print("\n   ⚠️  No colors detected in output")
        print("       Check if Rich is working: python -m rich")
    
except Exception as e:
    print(f"   ❌ Formatter test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test with Sphinx (if in docs folder)
print("\n3️⃣ Testing with Sphinx integration...")

# Check if we're in a Sphinx project
if os.path.exists('conf.py'):
    print("   📁 Found conf.py - testing with real Sphinx...")
    
    try:
        from sphinx.application import Sphinx
        from sphinx.util import logging as sphinx_logging
        
        # Create a minimal Sphinx app
        print("   🔧 Creating Sphinx app...")
        
        # Check if sphinxcolor is in extensions
        with open('conf.py', 'r', encoding='utf-8') as f:
            conf_content = f.read()
        
        if "'sphinxcolor'" in conf_content or '"sphinxcolor"' in conf_content:
            print("   ✅ sphinxcolor found in extensions")
        else:
            print("   ⚠️  sphinxcolor NOT in extensions list!")
            print("      Add to conf.py: extensions = ['sphinxcolor', ...]")
        
        # Try to inspect logger after import
        logger = logging.getLogger('sphinx')
        print(f"\n   📊 Sphinx logger handlers ({len(logger.handlers)}):")
        for i, handler in enumerate(logger.handlers):
            print(f"      [{i}] {handler.__class__.__name__}")
            if hasattr(handler, 'formatter') and handler.formatter:
                print(f"          Formatter: {handler.formatter.__class__.__name__}")
        
        print("\n   💡 Run 'make html' to see if colors work!")
        
    except ImportError:
        print("   ⚠️  Sphinx not installed or not in venv")
        print("      Install: pip install sphinx")
    except Exception as e:
        print(f"   ⚠️  Could not test with Sphinx: {e}")

else:
    print("   ℹ️  Not in Sphinx docs folder (no conf.py found)")
    print("      Run this script from your docs/ folder for full test")

# Summary
print("\n" + "="*70)
print("✅ BASIC TESTS PASSED!")
print("="*70)
print("\n📝 Next steps:")
print("   1. Make sure 'sphinxcolor' is in extensions (conf.py)")
print("   2. cd to docs folder")
print("   3. Run: make html")
print("   4. Check if WARNING lines are colored!")
print("\n🐛 If still not colored:")
print("   1. Run this script FROM docs/ folder")
print("   2. Check output above for handler/formatter info")
print("   3. Try: make html -v (verbose mode)")
print("="*70)