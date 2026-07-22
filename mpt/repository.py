from pathlib import Path

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
