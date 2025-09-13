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
    - Tagged release: "0.1.1.abc123f" (base version + short SHA)
    - Development: "0.1.1.abc123f" (same format for consistency)
    - Fallback: "0.1.1.unknown" if Git is not available
    
    Returns:
        Version string in format: BASE_VERSION.SHA
    """
    global _cached_version
    
    if _cached_version is not None:
        return _cached_version
    
    # Get base version from pyproject.toml fallback_version
    base_version = "0.1.1"
    
    try:
        # Try to get setuptools-scm version first to extract base version
        scm_version = metadata.version("mcp-rag")
        logger.debug(f"Raw setuptools-scm version: {scm_version}")
        
        # Extract base version from setuptools-scm version (remove dev/post/local parts)
        # Handle formats like: 0.1.31.post0.dev123+g925f4ee, 0.1.31, 0.1.31.post0, etc.
        base_match = scm_version.split('.dev')[0].split('.post')[0].split('+')[0]
        
        # Take only the first 3 parts (major.minor.patch)
        version_parts = base_match.split('.')
        if len(version_parts) >= 3:
            base_version = f"{version_parts[0]}.{version_parts[1]}.{version_parts[2]}"
        logger.debug(f"Extracted base version: {base_version}")
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