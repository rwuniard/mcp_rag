#!/usr/bin/env python3
"""
Simple HTML Coverage Runner for MCP RAG Project

This script runs tests and generates ONLY HTML coverage reports.
No XML or JSON files are created.

Usage:
    python run_html_coverage.py [--open]

Options:
    --open    Open the HTML report in browser after generation
"""

import subprocess
import sys
import webbrowser
from pathlib import Path


def main():
    """Run tests and generate HTML coverage report only."""
    print("🧪 Running tests with HTML coverage report...")
    
    # Check if --open flag is provided
    open_browser = "--open" in sys.argv
    
    try:
        # Run pytest with HTML coverage only
        result = subprocess.run([
            "uv", "run", "pytest", 
            "--cov=src", 
            "--cov-report=html", 
            "-q"
        ], check=True, cwd=Path(__file__).parent)
        
        html_path = Path(__file__).parent / "htmlcov" / "index.html"
        
        print("✅ Tests completed successfully!")
        print(f"📄 HTML coverage report: {html_path}")
        
        if open_browser and html_path.exists():
            print("🌐 Opening HTML report in browser...")
            webbrowser.open(f"file://{html_path.absolute()}")
            print("✅ HTML report opened!")
        else:
            print(f"💡 Open in browser: file://{html_path.absolute()}")
            
        print("\n🎯 Only htmlcov/ directory created - no coverage.xml or coverage.json!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()