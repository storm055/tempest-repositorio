from pathlib import Path

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
