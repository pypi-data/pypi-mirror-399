"""
TSPKG Loader

Responsible for decrypting, decompressing, and dynamically loading tspkg files.
"""

import os
import json
import tempfile
import zipfile
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import shutil

from tspkg_base.loader.security import decrypt_file

logger = logging.getLogger(__name__)


def load_tspkg(
    pkg_path: str,
    key: Optional[str] = None,
    cleanup_temp: bool = True
) -> None:
    """
    Load tspkg file

    Loading process:
    1. Read ZIP file
    2. Read manifest.json (if exists)
    3. Extract to temporary directory
    4. Decrypt files (if encrypted)
    5. Dynamically load Python modules
    6. Clean up temporary files (if cleanup_temp=True)

    Args:
        pkg_path: Path to tspkg file
        key: Decryption key (optional), if None then use environment variable or default key
        cleanup_temp: Whether to clean up temporary files after loading (default True)

    Raises:
        FileNotFoundError: If tspkg file doesn't exist
        ValueError: If file format is incorrect
        zipfile.BadZipFile: If ZIP file is corrupted

    Example:
        load_tspkg("my_package.tspkg", key="my_secret_key")
    """
    if not os.path.exists(pkg_path):
        raise FileNotFoundError(f"TSPKG file not found: {pkg_path}")

    pkg_path = os.path.abspath(pkg_path)
    logger.info(f"Loading TSPKG: {pkg_path}")

    # Read ZIP file
    try:
        with zipfile.ZipFile(pkg_path, 'r') as zip_ref:
            # Read manifest.json (if exists)
            manifest = _read_manifest(zip_ref)

            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="tspkg_")
            logger.debug(f"Created temporary directory: {temp_dir}")

            try:
                # Extract all files
                zip_ref.extractall(temp_dir)
                logger.debug(f"Extracted TSPKG to: {temp_dir}")

                # Decrypt files (if needed)
                if manifest.get("encrypted", False):
                    _decrypt_files(temp_dir, manifest, key)

                # Dynamically load modules
                _load_modules(temp_dir, manifest)

                logger.info(f"Successfully loaded TSPKG: {pkg_path}")

            finally:
                # Clean up temporary files
                if cleanup_temp:
                    try:
                        shutil.rmtree(temp_dir)
                        logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")
                else:
                    logger.debug(f"Temporary directory kept: {temp_dir}")

    except zipfile.BadZipFile as e:
        raise ValueError(f"Invalid TSPKG file format (not a valid ZIP): {e}")


def _read_manifest(zip_ref: zipfile.ZipFile) -> Dict[str, Any]:
    """
    Read manifest.json

    Args:
        zip_ref: ZIP file object

    Returns:
        Manifest dictionary, returns default values if not found
    """
    default_manifest = {
        "name": "unknown",
        "version": "1.0.0",
        "encrypted": False,
        "encryption_method": "simple",
        "entry_point": None
    }

    try:
        manifest_data = zip_ref.read("manifest.json")
        manifest = json.loads(manifest_data.decode('utf-8'))
        # Merge with defaults to ensure all fields exist
        return {**default_manifest, **manifest}
    except KeyError:
        logger.debug("manifest.json not found, using defaults")
        return default_manifest
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse manifest.json: {e}, using defaults")
        return default_manifest


def _decrypt_files(
    temp_dir: str,
    manifest: Dict[str, Any],
    key: Optional[str] = None
) -> None:
    """
    Decrypt files

    Args:
        temp_dir: Temporary directory path
        manifest: Manifest dictionary
        key: Decryption key (optional)
    """
    encryption_method = manifest.get("encryption_method", "simple")
    code_dir = os.path.join(temp_dir, "code")

    if not os.path.exists(code_dir):
        logger.warning(f"Code directory not found: {code_dir}")
        return

    logger.debug(f"Decrypting files in {code_dir} using method: {encryption_method}")

    # Traverse all files in code directory
    for root, dirs, files in os.walk(code_dir):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Decrypt all .py files or .py.enc files
            # If filename ends with .py.enc, decrypt and rename to .py
            if filename.endswith('.py.enc'):
                try:
                    # Decrypt file
                    decrypt_file(file_path, key=key)

                    # Rename to .py
                    new_name = filename.replace('.py.enc', '.py')
                    new_path = os.path.join(root, new_name)
                    os.rename(file_path, new_path)
                    logger.debug(f"Decrypted and renamed {file_path} to {new_path}")

                except Exception as e:
                    logger.error(f"Failed to decrypt file {file_path}: {e}")
                    raise
            elif filename.endswith('.py'):
                # If file is already .py but content is encrypted, decrypt directly
                try:
                    decrypt_file(file_path, key=key)
                    logger.debug(f"Decrypted file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to decrypt file {file_path}: {e}")
                    raise


def _load_modules(temp_dir: str, manifest: Dict[str, Any]) -> None:
    """
    Dynamically load Python modules

    Args:
        temp_dir: Temporary directory path
        manifest: Manifest dictionary
    """
    code_dir = os.path.join(temp_dir, "code")

    if not os.path.exists(code_dir):
        logger.warning(f"Code directory not found: {code_dir}")
        return

    entry_point = manifest.get("entry_point")

    if entry_point:
        # If entry point is specified, only load that module
        _load_module_by_entry_point(temp_dir, entry_point)
    else:
        # Otherwise load all .py files in code directory
        _load_all_modules(code_dir)


def _load_module_by_entry_point(temp_dir: str, entry_point: str) -> None:
    """
    Load module by entry point

    Args:
        temp_dir: Temporary directory path
        entry_point: Entry point module path (e.g., "code.main")
    """
    # Convert entry point path to file path
    # "code.main" -> "code/main.py"
    module_path = entry_point.replace('.', os.sep) + '.py'
    file_path = os.path.join(temp_dir, module_path)

    if not os.path.exists(file_path):
        logger.warning(f"Entry point file not found: {file_path}")
        return

    _load_module_file(file_path, temp_dir)


def _load_all_modules(code_dir: str) -> None:
    """
    Load all Python modules in code directory

    Args:
        code_dir: Code directory path
    """
    for root, dirs, files in os.walk(code_dir):
        # Skip __pycache__ directory
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for filename in files:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                _load_module_file(file_path, code_dir)


def _load_module_file(file_path: str, base_path: str) -> None:
    """
    Load a single Python module file

    Args:
        file_path: Python file path
        base_path: Base path (used to calculate module name)
    """
    # Calculate module name (relative to base_path)
    rel_path = os.path.relpath(file_path, base_path)
    module_name = rel_path.replace(os.sep, '.').replace('.py', '')

    logger.debug(f"Loading module: {module_name} from {file_path}")

    try:
        # Use importlib to dynamically load module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Failed to create spec for {file_path}")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        logger.debug(f"Successfully loaded module: {module_name}")

    except Exception as e:
        logger.error(f"Failed to load module {module_name} from {file_path}: {e}", exc_info=True)
        # Don't raise exception, continue loading other modules

