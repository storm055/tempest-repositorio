import json
from pathlib import Path

REPO_DIR_NAME = '.mpt'
PACKAGES_DIR_NAME = 'packages'
ROOTFS_DIR_NAME = 'rootfs'
INDEX_FILE_NAME = 'index.json'
DB_FILE_NAME = 'installed.json'


def repo_root(root=None):
    if root:
        return Path(root).expanduser().resolve()
    return Path.cwd().resolve()


def repo_dir(root=None):
    return repo_root(root) / REPO_DIR_NAME


def packages_dir(root=None):
    return repo_root(root) / PACKAGES_DIR_NAME


def rootfs_dir(root=None):
    return repo_root(root) / ROOTFS_DIR_NAME


def index_path(root=None):
    return repo_dir(root) / INDEX_FILE_NAME


def db_path(root=None):
    return repo_dir(root) / DB_FILE_NAME


def ensure_repo(root=None):
    root = repo_root(root)
    repo = repo_dir(root)
    repo.mkdir(parents=True, exist_ok=True)
    packages_dir(root).mkdir(parents=True, exist_ok=True)
    rootfs_dir(root).mkdir(parents=True, exist_ok=True)

    if not index_path(root).exists():
        index_path(root).write_text(json.dumps({'packages': {}}, indent=2), encoding='utf-8')
    if not db_path(root).exists():
        db_path(root).write_text(json.dumps({'installed': {}}, indent=2), encoding='utf-8')
