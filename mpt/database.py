from datetime import datetime
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
