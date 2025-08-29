#!/usr/bin/env python3
"""
Test Coverage Runner for MCP RAG Project

This script provides a convenient way to run all unit tests and generate
comprehensive coverage reports in multiple formats.

Usage:
    python run_coverage.py [options]

Options:
    --html-only     Generate only HTML coverage report
    --console-only  Generate only console coverage report
    --no-html       Skip HTML report generation
    --open          Open HTML report in browser after generation
    --help, -h      Show this help message

Examples:
    python run_coverage.py                    # Full coverage with HTML and console reports
    python run_coverage.py --open            # Generate reports and open HTML in browser
    python run_coverage.py --console-only    # Only console report
    python run_coverage.py --no-html         # Skip HTML generation
"""

import argparse
import subprocess
import sys
import time
import webbrowser

from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            check=False,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True, result.stdout, result.stderr
        print(f"❌ {description} failed")
        print(f"Error: {result.stderr}")
        return False, result.stdout, result.stderr

    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False, "", str(e)


def show_header():
    """Display script header."""
    print("=" * 60)
    print("🧪 MCP RAG Project - Test Coverage Runner")
    print("=" * 60)
    print()


def show_summary(total_tests, coverage_percent, duration):
    """Display summary statistics."""
    print()
    print("=" * 60)
    print("📊 COVERAGE SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Run: {total_tests}")
    print(f"📈 Coverage: {coverage_percent}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print("=" * 60)


def extract_test_count(output):
    """Extract test count from unittest output."""
    lines = output.split("\n")
    for line in lines:
        if line.startswith("Ran ") and " tests in " in line:
            # Extract number from "Ran X tests in Y.YYYs"
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]  # The test count
    return "Unknown"


def extract_coverage_percent(output):
    """Extract coverage percentage from coverage report."""
    lines = output.split("\n")
    for line in lines:
        if line.startswith("TOTAL") and "%" in line:
            # Extract percentage from the TOTAL line
            parts = line.split()
            for part in parts:
                if part.endswith("%"):
                    return part
    return "Unknown"


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Run tests and generate coverage reports for MCP RAG project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_coverage.py                    # Full coverage with HTML and console reports
  python run_coverage.py --open            # Generate reports and open HTML in browser  
  python run_coverage.py --console-only    # Only console report
  python run_coverage.py --no-html         # Skip HTML generation
        """,
    )

    parser.add_argument(
        "--html-only", action="store_true", help="Generate only HTML coverage report"
    )
    parser.add_argument(
        "--console-only",
        action="store_true",
        help="Generate only console coverage report",
    )
    parser.add_argument(
        "--no-html", action="store_true", help="Skip HTML report generation"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open HTML report in browser after generation",
    )

    args = parser.parse_args()

    # Validate conflicting options
    if args.html_only and args.console_only:
        print("❌ Error: --html-only and --console-only cannot be used together")
        return 1

    if args.html_only and args.no_html:
        print("❌ Error: --html-only and --no-html cannot be used together")
        return 1

    start_time = time.time()
    show_header()

    # Step 1: Run tests with coverage
    print("📋 Running comprehensive test suite with coverage tracking...")
    success, test_output, test_error = run_command(
        "uv run coverage run --source=src -m unittest discover tests -v",
        "Test execution with coverage tracking",
    )

    if not success:
        print("\n⚠️ Some tests failed, but coverage was still collected.")
        print("📊 Continuing with coverage report generation...")
        # Don't abort on test failures - coverage was still collected

    # Extract test statistics
    total_tests = extract_test_count(test_output)

    # Step 2: Generate console coverage report (unless html-only)
    console_output = ""
    coverage_percent = "Unknown"

    if not args.html_only:
        print("\n📊 Generating console coverage report...")
        success, console_output, console_error = run_command(
            "uv run coverage report --show-missing",
            "Console coverage report generation",
        )

        if success:
            coverage_percent = extract_coverage_percent(console_output)
            if not args.console_only and not args.no_html:
                print("\n" + "=" * 60)
                print("📋 COVERAGE REPORT")
                print("=" * 60)
            print(console_output)
        else:
            print("❌ Console coverage report generation failed")
            if console_error:
                print(f"Error: {console_error}")

    # Step 3: Generate HTML coverage report (unless console-only or no-html)
    html_path = None
    if not args.console_only and not args.no_html:
        print("\n🌐 Generating HTML coverage report...")
        success, _, html_error = run_command(
            "uv run coverage html", "HTML coverage report generation"
        )

        if success:
            html_path = Path(__file__).parent / "htmlcov" / "index.html"
            print(f"📄 HTML report generated: {html_path}")

            # Open in browser if requested
            if args.open:
                print("🌐 Opening HTML report in default browser...")
                try:
                    webbrowser.open(f"file://{html_path.absolute()}")
                    print("✅ HTML report opened in browser")
                except Exception as e:
                    print(f"⚠️  Could not open browser: {e}")
                    print(f"💡 Manually open: {html_path}")
        else:
            print("❌ HTML coverage report generation failed")
            if html_error:
                print(f"Error: {html_error}")

    # Step 4: Show summary
    duration = time.time() - start_time
    show_summary(total_tests, coverage_percent, duration)

    # Step 5: Show next steps
    print("\n💡 NEXT STEPS:")
    if html_path and html_path.exists() and not args.open:
        print(f"   • Open HTML report: open {html_path}")
        print(f"   • Or in browser: file://{html_path.absolute()}")

    print("   • View detailed line-by-line coverage in HTML report")
    print("   • Focus on files with <85% coverage for improvement")
    print(
        "   • Run specific test: python -m unittest tests.test_module.TestClass.test_method"
    )

    print("\n✨ Coverage analysis complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
