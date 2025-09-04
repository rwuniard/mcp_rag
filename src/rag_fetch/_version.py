"""
Version information for rag_fetch package.

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
    - Tagged release: "1.0.0"
    - Development: "1.0.0.dev5+g022f80b" (5 commits after tag + SHA)
    - Fallback: "1.0.0.unknown" if Git is not available
    
    Returns:
        Version string with Git SHA information when available.
    """
    global _cached_version
    
    if _cached_version is not None:
        return _cached_version
    
    try:
        # Try to get version from setuptools-scm via metadata
        _cached_version = metadata.version("mcp-rag")
        logger.debug(f"Version from metadata: {_cached_version}")
    except metadata.PackageNotFoundError:
        # Fallback for development environments
        git_sha = get_git_sha()
        if git_sha:
            dirty_suffix = ".dirty" if is_git_dirty() else ""
            _cached_version = f"0.1.0.dev+g{git_sha}{dirty_suffix}"
            logger.debug(f"Version from Git fallback: {_cached_version}")
        else:
            _cached_version = "0.1.0.unknown"
            logger.warning("Unable to determine version - using fallback")
    
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