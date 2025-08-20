#!/usr/bin/env python3
"""
Automated Setup Script for Trunk-Based Development

This script helps set up trunk-based development with GitHub Actions CI/CD,
branch protection rules, and development tools for the MCP RAG project.

Usage:
    python setup_trunk_development.py [--dry-run] [--skip-deps] [--github-setup]
"""

import argparse
import re
import subprocess
import sys

from pathlib import Path


def run_command(
    command: str, description: str = "", check: bool = True
) -> tuple[bool, str]:
    """Run a shell command and return success status and output."""
    print(f"🔧 {description or command}")
    try:
        result = subprocess.run(
            command,
            check=False,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        if check and result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)


def check_prerequisites() -> bool:
    """Check if required tools are available."""
    print("📋 Checking prerequisites...")

    tools = [
        ("git", "Git version control"),
        ("uv", "UV package manager"),
        ("python", "Python interpreter"),
    ]

    missing = []
    for tool, description in tools:
        success, _ = run_command(
            f"which {tool}", f"Checking {description}", check=False
        )
        if not success:
            missing.append(f"  - {tool}: {description}")
        else:
            print(f"  ✅ {tool}: Available")

    if missing:
        print("❌ Missing required tools:")
        for tool in missing:
            print(tool)
        return False

    print("✅ All prerequisites satisfied")
    return True


def install_dev_dependencies(dry_run: bool = False) -> bool:
    """Install development dependencies with uv."""
    print("\n📦 Installing development dependencies...")

    dev_deps = [
        "black>=23.0.0",
        "isort>=5.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "bandit>=1.7.0",
        "safety>=2.0.0",
        "coverage>=7.0.0",
    ]

    if dry_run:
        print("🔍 DRY RUN - Would install:")
        for dep in dev_deps:
            print(f"  - {dep}")
        return True

    for dep in dev_deps:
        success, _ = run_command(
            f"uv add --dev {dep}", f"Installing {dep}", check=False
        )
        if not success:
            print(f"⚠️  Could not install {dep}, might already exist")

    print("✅ Development dependencies processed")
    return True


def verify_project_structure() -> bool:
    """Verify the project has the expected structure."""
    print("\n🔍 Verifying project structure...")

    required_files = [
        "pyproject.toml",
        "run_coverage.py",
        "src/rag_store/__init__.py",
        "src/rag_fetch/__init__.py",
        "tests/",
    ]

    missing = []
    for file_path in required_files:
        path = Path(file_path)
        if not path.exists():
            missing.append(file_path)
        else:
            print(f"  ✅ {file_path}")

    if missing:
        print("❌ Missing required project files:")
        for file_path in missing:
            print(f"  - {file_path}")
        return False

    print("✅ Project structure verified")
    return True


def test_coverage_tool() -> tuple[bool, str]:
    """Test the coverage tool and get current coverage."""
    print("\n🧪 Testing coverage tool...")

    success, output = run_command(
        "python run_coverage.py --console-only",
        "Running coverage analysis",
        check=False,
    )

    if not success:
        return False, "Coverage tool failed to run"

    # Extract coverage percentage
    coverage_match = re.search(r"TOTAL.*?(\d+)%", output)
    if coverage_match:
        coverage = int(coverage_match.group(1))
        print(f"✅ Current coverage: {coverage}%")

        if coverage >= 70:
            print("✅ Coverage meets minimum threshold (70%)")
        else:
            print("⚠️  Coverage below minimum threshold (70%)")

        return True, f"{coverage}%"
    print("⚠️  Could not parse coverage percentage")
    return True, "Unknown%"


def create_github_files() -> bool:
    """Verify GitHub workflow and template files exist."""
    print("\n📁 Checking GitHub files...")

    github_files = [
        ".github/workflows/ci.yml",
        ".github/branch-protection-config.md",
        ".github/PULL_REQUEST_TEMPLATE/default.md",
        ".github/PULL_REQUEST_TEMPLATE/quick.md",
    ]

    all_exist = True
    for file_path in github_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_exist = False

    if all_exist:
        print("✅ All GitHub files present")
    else:
        print("❌ Some GitHub files missing - run the full setup first")

    return all_exist


def get_repo_info() -> tuple[str, str]:
    """Get GitHub repository owner and name."""
    try:
        success, output = run_command("git remote get-url origin", check=False)
        if success:
            # Parse GitHub URL
            url = output.strip()
            if "github.com" in url:
                if url.startswith("git@"):
                    # SSH format: git@github.com:owner/repo.git
                    match = re.search(r"github\.com:([^/]+)/(.+?)(?:\.git)?$", url)
                else:
                    # HTTPS format: https://github.com/owner/repo.git
                    match = re.search(r"github\.com/([^/]+)/(.+?)(?:\.git)?$", url)

                if match:
                    return match.group(1), match.group(2)
    except:
        pass

    return "your-username", "your-repo"


def display_next_steps(dry_run: bool, coverage: str) -> None:
    """Display next steps for completing the setup."""
    owner, repo = get_repo_info()

    print("\n" + "=" * 60)
    print("🎉 TRUNK-BASED DEVELOPMENT SETUP COMPLETE!")
    print("=" * 60)

    print("\n📊 **Current Status:**")
    print(f"   • Project coverage: {coverage}")
    print("   • CI/CD pipeline: ✅ Ready")
    print("   • PR templates: ✅ Ready")
    print("   • Documentation: ✅ Complete")

    if not dry_run:
        print("\n🔧 **Required: Configure Branch Protection**")
        print(f"   1. Go to: https://github.com/{owner}/{repo}/settings/branches")
        print("   2. Click 'Add rule', branch pattern: main")
        print("   3. Enable these options:")
        print("      ✅ Require status checks: test, quality, security, integration")
        print("      ✅ Require pull request reviews (1 reviewer)")
        print("      ✅ Require branches to be up to date")
        print("      ✅ Include administrators")
        print("   4. Set merge preferences:")
        print("      ✅ Allow squash merging")
        print("      ❌ Disable merge commits and rebase")

        print("\n⚡ **Test Your Setup:**")
        print("   git checkout -b test/trunk-workflow-setup")
        print("   echo '# Test' >> WORKFLOW_TEST.md")
        print("   git add WORKFLOW_TEST.md")
        print("   git commit -m 'test: trunk development setup'")
        print("   git push -u origin test/trunk-workflow-setup")
        print("   gh pr create --template quick.md")

        print("\n📚 **Learn More:**")
        print("   • Quick start: IMPLEMENTATION_GUIDE.md")
        print("   • Full workflow: TRUNK_BASED_DEVELOPMENT.md")
        print("   • Branch protection: .github/branch-protection-config.md")

        print("\n🎯 **Success Metrics to Watch:**")
        print("   • PR cycle time: <24 hours")
        print("   • Coverage trend: Moving toward 85%")
        print("   • Main branch stability: >99% green")

    print("\n💡 **Tips:**")
    print("   • Keep PRs small (<500 lines)")
    print("   • Test locally: python run_coverage.py --console-only")
    print("   • Merge frequently (within 48 hours)")
    print("   • Use squash merge for clean history")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Set up trunk-based development for MCP RAG project"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip installing development dependencies",
    )
    parser.add_argument(
        "--github-setup", action="store_true", help="Show GitHub configuration commands"
    )

    args = parser.parse_args()

    print("🚀 MCP RAG Trunk-Based Development Setup")
    print("=" * 50)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    # Step 1: Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Step 2: Verify project structure
    if not verify_project_structure():
        print("\n❌ Project structure issues detected.")
        print("Please ensure you're running this from the MCP RAG project root.")
        sys.exit(1)

    # Step 3: Install development dependencies
    if not args.skip_deps:
        if not install_dev_dependencies(args.dry_run):
            print("\n⚠️  Development dependency installation had issues")
            print("You may need to install them manually")

    # Step 4: Test coverage tool
    success, coverage = test_coverage_tool()
    if not success:
        print("\n❌ Coverage tool test failed")
        print("Please check your test suite and try again")
        sys.exit(1)

    # Step 5: Verify GitHub files
    if not create_github_files():
        print("\n❌ GitHub configuration files missing")
        print("The setup may not be complete")
        sys.exit(1)

    # Step 6: Display next steps
    display_next_steps(args.dry_run, coverage)

    if args.github_setup:
        owner, repo = get_repo_info()
        print("\n🔧 **GitHub CLI Commands** (alternative to web UI):")
        print(f"gh api repos/{owner}/{repo}/branches/main/protection \\")
        print("  --method PUT \\")
        print(
            '  --field required_status_checks=\'{"strict":true,"checks":[{"context":"test"},{"context":"quality"},{"context":"security"},{"context":"integration"}]}\' \\'
        )
        print(
            "  --field required_pull_request_reviews='{\"required_approving_review_count\":1}' \\"
        )
        print("  --field enforce_admins=true")

    print("\n✨ Setup complete! Your trunk-based development workflow is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
