from pathlib import Path

from .config import rootfs_dir
from .database import InstalledDatabase


def remove_package(name, repo_root=None):
    repo_root = Path(repo_root).expanduser().resolve() if repo_root else None
    db = InstalledDatabase(repo_root)
    record = db.get_package(name)
    if not record:
        raise KeyError(f'Package not installed: {name}')

    root = rootfs_dir(repo_root)
    for file_path in sorted(record.get('files', []), reverse=True):
        target = root / file_path
        if target.exists():
            if target.is_file() or target.is_symlink():
                target.unlink()
            elif target.is_dir():
                try:
                    target.rmdir()
                except OSError:
                    pass

    for directory in sorted({(root / Path(path)).parent for path in record.get('files', [])}, reverse=True):
        try:
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
        except OSError:
            pass

    db.remove_package(name)
