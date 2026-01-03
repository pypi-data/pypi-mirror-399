"""Backup and restore helpers"""
from pathlib import Path
import shutil
from typing import Optional


def create_backup(path: str) -> str:
    """
    Create a backup of the file at `path` with a `.bak` extension.
    Overwrites any existing backup.
    Returns the backup file path.
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Cannot backup non-existent file: {path}")
    bak = src.with_suffix(src.suffix + ".bak")
    shutil.copy2(src, bak)  # copy2 preserves metadata
    return str(bak)


def restore_backup(path: str) -> Optional[str]:
    """
    Restore the `.bak` backup for the given file.
    Returns the restored file path if successful, None if no backup exists.
    """
    src = Path(path)
    bak = src.with_suffix(src.suffix + ".bak")
    if bak.exists():
        shutil.copy2(bak, src)
        return str(src)
    return None