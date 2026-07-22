import argparse
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
