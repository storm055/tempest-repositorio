import tarfile
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
