from pathlib import Path

root = Path('/home/qprisma/tempest-repositorio')
files = {
    'mpt/__init__.py': '''"""Minimal Package Tool (mpt) for source-based Linux repositories."""

from .main import main
''',
    'mpt/config.py': '''import json
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
''',
    'mpt/utils.py': '''import json
import os
import shutil
import subprocess
from pathlib import Path


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def run_shell(command, cwd=None, env=None):
    if isinstance(command, list):
        command = ' && '.join(command)
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env={**os.environ, **(env or {})},
        shell=True,
        check=True,
    )
    return result.returncode


def copy_tree(src, dst):
    src = Path(src)
    dst = Path(dst)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def relpath(path, start=None):
    return str(Path(path).resolve().relative_to(Path(start).resolve()))
''',
    'mpt/package.py': '''from pathlib import Path

from .utils import load_json


class Package:
    def __init__(self, data, manifest_path=None):
        self.data = data
        self.manifest_path = Path(manifest_path).resolve() if manifest_path else None
        self.name = data.get('name')
        self.version = data.get('version')
        self.description = data.get('description', '')
        self.source = data.get('source')
        self.build_commands = data.get('build_commands', [])
        self.dependencies = data.get('dependencies', [])

        if not self.name or not self.version:
            raise ValueError('Package manifest must include name and version.')

    @classmethod
    def load(cls, manifest_path):
        manifest_path = Path(manifest_path).expanduser().resolve()
        raw = load_json(manifest_path)
        if raw is None:
            raise FileNotFoundError(f'Package manifest not found: {manifest_path}')
        return cls(raw, manifest_path=manifest_path)

    def to_dict(self):
        return self.data

    def metadata(self):
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'source': self.source,
            'dependencies': self.dependencies,
            'build_commands': self.build_commands,
        }
''',
    'mpt/repository.py': '''from pathlib import Path

from .config import ensure_repo, index_path, packages_dir
from .package import Package
from .utils import load_json, save_json


class Repository:
    def __init__(self, root=None):
        self.root = Path(root).expanduser().resolve() if root else None
        ensure_repo(self.root)
        self.root = self.root or Path.cwd().resolve()
        self.index = load_json(index_path(self.root), default={'packages': {}})

    def save(self):
        save_json(index_path(self.root), self.index)

    def list_packages(self):
        return {name: info for name, info in self.index.get('packages', {}).items()}

    def find_package(self, name):
        package_info = self.index.get('packages', {}).get(name)
        if not package_info:
            return None
        manifest_path = Path(self.root) / package_info['path']
        return Package.load(manifest_path)

    def add_manifest(self, manifest_path):
        manifest_path = Path(manifest_path).expanduser().resolve()
        package = Package.load(manifest_path)

        packages_root = packages_dir(self.root)
        packages_root.mkdir(parents=True, exist_ok=True)
        destination = packages_root / f'{package.name}-{package.version}.json'

        if destination.exists() and destination.resolve() != manifest_path:
            raise FileExistsError(f'Package manifest already exists: {destination}')

        if manifest_path != destination:
            destination.write_text(json.dumps(package.data, indent=2, ensure_ascii=False), encoding='utf-8')

        self.index['packages'][package.name] = {
            'version': package.version,
            'path': str(destination.relative_to(self.root)),
        }
        self.save()
        return package
''',
    'mpt/database.py': '''from datetime import datetime
from pathlib import Path

from .config import db_path, ensure_repo
from .utils import load_json, save_json


class InstalledDatabase:
    def __init__(self, root=None):
        self.root = Path(root).expanduser().resolve() if root else None
        ensure_repo(self.root)
        self.root = self.root or Path.cwd().resolve()
        self.path = db_path(self.root)
        self.data = load_json(self.path, default={'installed': {}})

    def save(self):
        save_json(self.path, self.data)

    def list_packages(self):
        return list(self.data.get('installed', {}).keys())

    def get_package(self, name):
        return self.data.get('installed', {}).get(name)

    def add_package(self, package, files):
        self.data.setdefault('installed', {})[package.name] = {
            'name': package.name,
            'version': package.version,
            'manifest': package.metadata(),
            'files': sorted(files),
            'dependencies': package.dependencies,
            'installed_at': datetime.utcnow().isoformat() + 'Z',
        }
        self.save()

    def remove_package(self, name):
        if name in self.data.get('installed', {}):
            del self.data['installed'][name]
            self.save()
''',
    'mpt/dependency.py': '''def missing_dependencies(package, installed_db):
    missing = []
    for dependency in package.dependencies:
        if not installed_db.get_package(dependency):
            missing.append(dependency)
    return missing
''',
    'mpt/download.py': '''import tarfile
import urllib.request
import zipfile
from pathlib import Path

from .utils import ensure_dir


def download_source(source, work_dir):
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    if source.startswith(('http://', 'https://', 'ftp://')):
        destination = work_dir / Path(source).name
        urllib.request.urlretrieve(source, destination)
        return destination

    source_path = Path(source).expanduser().resolve()
    if source_path.exists():
        return source_path

    raise FileNotFoundError(f'Source not found: {source}')


def extract_archive(archive_path, destination):
    archive_path = Path(archive_path)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    if archive_path.suffix == '.zip':
        with zipfile.ZipFile(archive_path, 'r') as archive:
            archive.extractall(destination)
        return destination

    with tarfile.open(archive_path, 'r:*') as archive:
        archive.extractall(destination)
    return destination


def prepare_source(package, work_dir):
    work_dir = Path(work_dir).expanduser().resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    source = package.source
    if not source:
        raise ValueError('Package manifest must include a source entry.')

    downloaded = download_source(source, work_dir)
    if downloaded.is_dir():
        return downloaded

    extracted = work_dir / 'source'
    extract_archive(downloaded, extracted)
    entries = [entry for entry in extracted.iterdir() if entry.is_dir()]
    if len(entries) == 1:
        return entries[0]
    return extracted
''',
    'mpt/install.py': '''import tempfile
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
''',
    'mpt/remove.py': '''from pathlib import Path

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
''',
    'mpt/verify.py': '''from pathlib import Path

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
''',
    'mpt/main.py': '''import argparse
import json
import sys

from .config import ensure_repo, repo_root
from .database import InstalledDatabase
from .install import install_package
from .repository import Repository
from .remove import remove_package
from .verify import verify_package


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog='mpt',
        description='mpt - Minimal Package Tool for a source-based Linux repository.',
    )
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('init', help='Initialize repository structure.')

    add_parser = subparsers.add_parser('add', help='Add a package manifest to the repository.')
    add_parser.add_argument('manifest', help='Path to a package manifest JSON file.')

    list_parser = subparsers.add_parser('list', help='List packages available in the repository.')
    list_parser.add_argument('--installed', action='store_true', help='Show installed packages instead of repository packages.')

    show_parser = subparsers.add_parser('show', help='Show package metadata.')
    show_parser.add_argument('name', help='Package name.')

    install_parser = subparsers.add_parser('install', help='Install a package into rootfs.')
    install_parser.add_argument('name', help='Package name.')

    remove_parser = subparsers.add_parser('remove', help='Remove an installed package.')
    remove_parser.add_argument('name', help='Package name.')

    verify_parser = subparsers.add_parser('verify', help='Verify installed package files.')
    verify_parser.add_argument('name', help='Package name.')

    return parser.parse_args(argv)


def command_init(args):
    ensure_repo(repo_root())
    print('Repository initialized at', repo_root())


def command_add(args):
    repo = Repository(repo_root())
    package = repo.add_manifest(args.manifest)
    print(f'Added package {package.name} version {package.version}')


def command_list(args):
    if args.installed:
        db = InstalledDatabase(repo_root())
        installed = db.list_packages()
        if not installed:
            print('No installed packages found.')
            return
        for name in installed:
            print(name)
        return

    repo = Repository(repo_root())
    packages = repo.list_packages()
    if not packages:
        print('No packages found in repository.')
        return
    for name, info in packages.items():
        print(f"{name} {info['version']} -> {info['path']}")


def command_show(args):
    repo = Repository(repo_root())
    package = repo.find_package(args.name)
    if not package:
        print(f'Package not found: {args.name}', file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(package.metadata(), indent=2, ensure_ascii=False))


def command_install(args):
    repo = Repository(repo_root())
    package = repo.find_package(args.name)
    if not package:
        print(f'Package not found: {args.name}', file=sys.stderr)
        raise SystemExit(1)

    files = install_package(package, repo_root())
    print(f'Installed {package.name} ({len(files)} files).')


def command_remove(args):
    try:
        remove_package(args.name, repo_root())
        print(f'Removed package {args.name}')
    except KeyError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)


def command_verify(args):
    try:
        missing = verify_package(args.name, repo_root())
        if not missing:
            print(f'Package {args.name} is complete.')
            return
        print(f'Package {args.name} has missing files:')
        for path in missing:
            print('  -', path)
    except KeyError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)


def main(argv=None):
    args = parse_args(argv)
    if args.command == 'init':
        command_init(args)
    elif args.command == 'add':
        command_add(args)
    elif args.command == 'list':
        command_list(args)
    elif args.command == 'show':
        command_show(args)
    elif args.command == 'install':
        command_install(args)
    elif args.command == 'remove':
        command_remove(args)
    elif args.command == 'verify':
        command_verify(args)
    else:
        parser = argparse.ArgumentParser(prog='mpt')
        parser.print_help()
        raise SystemExit(1)


if __name__ == '__main__':
    main()
''',
    'README.md': '''# MPT - Gerenciador de Pacotes para LFS (mpt)

Este repositório contém o projeto `mpt`, um gerenciador de pacotes minimalista para distros Linux baseadas em código-fonte.

## Estrutura

- `mpt/`: código do gerenciador de pacotes
- `packages/`: metadados e definições de pacotes
- `rootfs/`: sistema de arquivos de destino onde os pacotes são instalados
- `.mpt/`: dados internos do repositório (`index.json`, `installed.json`)

## Como usar

Inicialize o repositório:

```bash
python3 -m mpt.main init
```

Adicione um manifest de pacote:

```bash
python3 -m mpt.main add packages/hello.json
```

Instale um pacote:

```bash
python3 -m mpt.main install hello
```

Liste os pacotes disponíveis:

```bash
python3 -m mpt.main list
```

Liste os pacotes instalados:

```bash
python3 -m mpt.main list --installed
```

Remova um pacote:

```bash
python3 -m mpt.main remove hello
```

Verifique os arquivos de um pacote instalado:

```bash
python3 -m mpt.main verify hello
```
''',
    'pyproject.toml': '''[project]
name = "mpt"
version = "0.1.0"
description = "Minimal package manager for a source-based Linux distribution repository."
requires-python = ">=3.11"

[project.scripts]
mpt = "mpt.main:main"
''',
    '.gitignore': '''__pycache__/
.mpt/
rootfs/
*.pyc
''',
    'packages/hello.json': '''{
  "name": "hello",
  "version": "2.12",
  "description": "Exemplo de pacote para o repositório mpt.",
  "source": "https://ftp.gnu.org/gnu/hello/hello-2.12.tar.gz",
  "build_commands": [
    "./configure --prefix=/usr",
    "make",
    "make install"
  ],
  "dependencies": []
}
''',
}

for relative_path, content in files.items():
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

print('scaffold written')
