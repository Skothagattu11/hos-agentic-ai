#!/usr/bin/env python3
"""
Wrapper script to handle Unicode encoding issues in Windows
Forces UTF-8 encoding and replaces problematic characters
"""
import sys
import os
import subprocess
import codecs

def main():
    # Force UTF-8 encoding for stdout and stderr
    if sys.platform == "win32":
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach(), errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach(), errors='replace')
    
    # Set environment variables for Unicode support
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Run the actual main_api.py script
    try:
        import main_api
        main_api.main()
    except UnicodeEncodeError as e:
        print(f"[ERROR] Unicode encoding error handled: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()