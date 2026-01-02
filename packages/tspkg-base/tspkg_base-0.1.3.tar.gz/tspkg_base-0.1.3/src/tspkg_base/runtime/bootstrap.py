"""
Bootstrap Module

Scans and loads all tspkg files when the application starts.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from tspkg_base.loader import load_tspkg

logger = logging.getLogger(__name__)


def bootstrap(
    tspkg_dir: Optional[str] = None,
    key: Optional[str] = None,
    cleanup_temp: bool = True
) -> Dict[str, Any]:
    """
    Load all tspkg files at startup

    Args:
        tspkg_dir: Directory path where tspkg files are located
                   If None, read from environment variable TSPKG_DIR
                   If environment variable is not set, use default value "./tspkgs"
        key: Decryption key (optional), if None then use environment variable or default key
        cleanup_temp: Whether to clean up temporary files after loading (default True)

    Returns:
        Dictionary containing loading results:
        - loaded: List of successfully loaded files
        - failed: List of failed files (contains error messages)
        - total: Total number of files

    Example:
        result = bootstrap(tspkg_dir="./tspkgs", key="my_secret_key")
        print(f"Loaded {len(result['loaded'])} packages")
    """
    if tspkg_dir is None:
        tspkg_dir = os.getenv("TSPKG_DIR", "./tspkgs")

    tspkg_path = Path(tspkg_dir)
    if not tspkg_path.exists():
        logger.warning(f"TSPKG directory not found: {tspkg_dir}")
        return {
            "loaded": [],
            "failed": [],
            "total": 0
        }

    logger.info(f"Bootstrap loading from: {tspkg_dir}")

    # Scan all .tspkg files in directory
    tspkg_files = list(tspkg_path.glob("*.tspkg"))
    
    if not tspkg_files:
        logger.info(f"No TSPKG files found in {tspkg_dir}")
        return {
            "loaded": [],
            "failed": [],
            "total": 0
        }

    logger.info(f"Found {len(tspkg_files)} TSPKG file(s)")

    loaded = []
    failed = []

    # Sort by filename to ensure consistent loading order
    tspkg_files.sort(key=lambda p: p.name)

    # Load one by one
    for pkg_file in tspkg_files:
        pkg_path = str(pkg_file.absolute())
        logger.info(f"Loading TSPKG: {pkg_file.name}")

        try:
            load_tspkg(pkg_path, key=key, cleanup_temp=cleanup_temp)
            loaded.append(pkg_file.name)
            logger.info(f"✓ Successfully loaded: {pkg_file.name}")
        except Exception as e:
            error_msg = f"{pkg_file.name}: {str(e)}"
            failed.append(error_msg)
            logger.error(f"✗ Failed to load {pkg_file.name}: {e}", exc_info=True)

    # Output loading summary
    logger.info(f"Bootstrap completed: {len(loaded)}/{len(tspkg_files)} packages loaded")
    if failed:
        logger.warning(f"Failed to load {len(failed)} package(s):")
        for error in failed:
            logger.warning(f"  - {error}")

    return {
        "loaded": loaded,
        "failed": failed,
        "total": len(tspkg_files)
    }


def list_tspkg_files(tspkg_dir: Optional[str] = None) -> List[str]:
    """
    List all tspkg files in directory

    Args:
        tspkg_dir: Directory path where tspkg files are located
                   If None, read from environment variable TSPKG_DIR
                   If environment variable is not set, use default value "./tspkgs"

    Returns:
        List of tspkg file names
    """
    if tspkg_dir is None:
        tspkg_dir = os.getenv("TSPKG_DIR", "./tspkgs")

    tspkg_path = Path(tspkg_dir)
    if not tspkg_path.exists():
        return []

    tspkg_files = list(tspkg_path.glob("*.tspkg"))
    return sorted([f.name for f in tspkg_files])

