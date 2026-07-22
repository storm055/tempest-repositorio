import tempfile
from pathlib import Path

from .config import rootfs_dir
from .database import InstalledDatabase
from .dependency import missing_dependencies
from .download import prepare_source
from .utils import ensure_dir, run_shell


def list_installed_files(root):
    root = Path(root)
    installed = []
    if not root.exists():
        return installed

    for path in root.rglob('*'):
        if path.is_file() or path.is_symlink():
            installed.append(str(path.relative_to(root)))
    return installed


def install_package(package, repo_root=None):
    repo_root = Path(repo_root).expanduser().resolve() if repo_root else None
    db = InstalledDatabase(repo_root)
    missing = missing_dependencies(package, db)
    if missing:
        raise RuntimeError(f"Missing dependencies: {', '.join(missing)}")

    destination = rootfs_dir(repo_root)
    ensure_dir(destination)

    with tempfile.TemporaryDirectory(prefix='mpt-build-') as tempdir:
        source_dir = prepare_source(package, tempdir)
        env = {
            'DESTDIR': str(destination),
            'PREFIX': '/usr',
        }

        for command in package.build_commands:
            run_shell(command, cwd=source_dir, env=env)

    files = list_installed_files(destination)
    db.add_package(package, files)
    return files
