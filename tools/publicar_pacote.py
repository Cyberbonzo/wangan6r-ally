#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Audit the explicit public file set and create a source-only release."""
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def audit():
    names = (ROOT / 'PUBLIC_FILES.txt').read_text().splitlines()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate public file')
    if (ROOT / '.git').exists():
        tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines())
        if tracked != set(names):
            raise ValueError('Tracked files differ from PUBLIC_FILES.txt: ' + str(tracked ^ set(names)))
    files = {}
    for name in names:
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or not path.is_file():
            raise ValueError('Invalid public file: ' + name)
        data = path.read_bytes()
        text = data.decode('utf-8')
        if len(data) > 250_000 or '\x00' in text:
            raise ValueError('Binary or oversized content: ' + name)
        if re.search(r'(?:github_pat_|gh[pousr]_)[A-Za-z0-9]{20,}', text):
            raise ValueError('Potential credential: ' + name)
        if re.search(r'192\.168\.\d+\.\d+|C:\\Users\\|/home/[^ /]+/', text):
            raise ValueError('Private machine path or address: ' + name)
        files[name] = data
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    files = audit()
    print(f'Public audit OK: {len(files)} explicit UTF-8 source/documentation files.')
    if args.check:
        return
    version = (ROOT / 'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Invalid version')
    args.output.mkdir(parents=True, exist_ok=True)
    archive = args.output / f'wangan6r-ally-{version}-source.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(f'wangan6r-ally-{version}/{name}', (2026, 11, 15, 0, 0, 0))
            entry.external_attr = (0o100755 if name.endswith('.sh') else 0o100644) << 16
            output.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (args.output / 'SHA256SUMS.txt').write_text(f'{checksum}  {archive.name}\n', encoding='utf-8')
    print(archive)


if __name__ == '__main__':
    main()
