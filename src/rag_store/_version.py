"""
Version information for rag_store package.

Provides dynamic version retrieval from Git using setuptools-scm,
with fallback handling for different deployment scenarios.
"""

import logging
import subprocess
from importlib import metadata
from typing import Optional

logger = logging.getLogger(__name__)

# Cached version to avoid repeated calculations
_cached_version: Optional[str] = None


def get_git_sha() -> Optional[str]:
    """Get the current Git SHA hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_git_branch() -> Optional[str]:
    """Get the current Git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def is_git_dirty() -> bool:
    """Check if there are uncommitted changes in the Git repository."""
    try:
        result = subprocess.run(
            ["git", "diff-index", "--quiet", "HEAD", "--"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode != 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_version() -> str:
    """
    Get the package version with Git integration.
    
    Returns version in format:
    - "0.1.1.abc123f" (base version from pyproject.toml + short SHA)
    - "0.1.1.unknown" if Git is not available
    
    Returns:
        Version string in format: BASE_VERSION.SHA
    """
    global _cached_version
    
    if _cached_version is not None:
        return _cached_version
    
    # Get base version from package metadata (pyproject.toml)
    base_version = "0.1.1"  # fallback
    
    try:
        # Get the static version from pyproject.toml 
        package_version = metadata.version("mcp-rag")
        # Use this as base version if it's a simple semantic version
        if package_version and len(package_version.split('.')) >= 3:
            base_version = package_version
        logger.debug(f"Base version from package: {base_version}")
    except metadata.PackageNotFoundError:
        logger.debug("Package not found in metadata, using fallback base version")
    
    # Always append Git SHA for traceability
    git_sha = get_git_sha()
    if git_sha:
        _cached_version = f"{base_version}.{git_sha}"
        logger.debug(f"Version with SHA: {_cached_version}")
    else:
        _cached_version = f"{base_version}.unknown"
        logger.warning("Unable to determine Git SHA - using unknown suffix")
    
    return _cached_version


def get_version_info() -> dict:
    """
    Get comprehensive version information.
    
    Returns:
        Dictionary containing version, Git SHA, branch, and dirty status.
    """
    return {
        "version": get_version(),
        "git_sha": get_git_sha(),
        "git_branch": get_git_branch(),
        "git_dirty": is_git_dirty(),
    }


# Make version available at module level
__version__ = get_version()