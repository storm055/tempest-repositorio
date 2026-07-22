from pathlib import Path

from .config import rootfs_dir
from .database import InstalledDatabase


def verify_package(name, repo_root=None):
    repo_root = Path(repo_root).expanduser().resolve() if repo_root else None
    db = InstalledDatabase(repo_root)
    record = db.get_package(name)
    if not record:
        raise KeyError(f'Package not installed: {name}')

    root = rootfs_dir(repo_root)
    missing = []
    for file_path in record.get('files', []):
        if not (root / file_path).exists():
            missing.append(file_path)
    return missing
