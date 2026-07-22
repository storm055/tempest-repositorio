import json
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
