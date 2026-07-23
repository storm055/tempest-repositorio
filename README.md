# MPT - Modular package tool for LFS (mpt)

This repository contains the `mpt` project, a minimalist package manager for source-based Linux distributions.

## Structure

- `mpt/`: package manager code
- `packages/`: package metadata and definitions
- `rootfs/`: target filesystem where packages are installed
- `.mpt/`: internal repository data (`index.json`, `installed.json`)

## Usage

Initialize the repository:

```bash
python3 -m mpt.main init
```

Add a package manifest:

```bash
python3 -m mpt.main add packages/hello.json
```

Install a package:

```bash
python3 -m mpt.main install hello
```

List available packages:

```bash
python3 -m mpt.main list
```

List installed packages:

```bash
python3 -m mpt.main list --installed
```

Remove a package:

```bash
python3 -m mpt.main remove hello
```

Verify the files of an installed package:

```bash
python3 -m mpt.main verify hello
```
