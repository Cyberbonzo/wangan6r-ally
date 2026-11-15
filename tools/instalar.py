#!/usr/bin/env python3
"""Prepare a private Linux installation from the user's game archive."""
import argparse,hashlib,shutil,tarfile,urllib.request,zipfile
from pathlib import Path

VERSION='0.1.0'
ARCHIVE='WanganLauncher-0.1.0-linux-x86_64.tar.gz'
RUNTIME_SHA='96dd8eaf13879332c6271ac3b9d3de341aabec768482b09528d5977ef3ef7918'
GAME_SHA='bf9fded65f5d029deaed5c3b5d06e8035dae70eee2e03c51e3adc2b1444ae2be'
UPSTREAM='https://github.com/akitaonrails/rea-teknoparrot-wangan-series'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-zip',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path.home()/'Games/Wangan6R')
    parser.add_argument('--runtime-archive',type=Path)
    parser.add_argument('--download-runtime',action='store_true')
    args=parser.parse_args();root=args.root.expanduser().resolve()
    if (root/'userdata').exists():raise SystemExit('Existing installation: preserve userdata and update source files separately.')
    for d in ('game','source/bin','logs','dependencias','runtime','artes'):(root/d).mkdir(parents=True,exist_ok=True)
    archive=args.runtime_archive
    if archive is None:
        archive=root/'dependencias'/ARCHIVE
        if not archive.exists():
            if not args.download_runtime:raise SystemExit('Supply --runtime-archive or --download-runtime.')
            urllib.request.urlretrieve(UPSTREAM+'/releases/download/v0.1.0/'+ARCHIVE,archive)
    assert sha(archive)==RUNTIME_SHA,'Runtime archive digest mismatch'
    with tarfile.open(archive) as t:
        members=[m for m in t.getmembers() if '/components/wal' not in m.name and '/components/openparrot-6rr' not in m.name]
        t.extractall(root/'runtime',members=members,filter='data')
    with zipfile.ZipFile(args.game_zip) as z:
        assert 'wmn6r.exe' in z.namelist(),'Expected 6R archive with wmn6r.exe at its root'
        assert hashlib.sha256(z.read('wmn6r.exe')).hexdigest()==GAME_SHA,'Unsupported game revision'
        for item in z.infolist():
            if item.is_dir() or item.filename.startswith('[SYSTEM]/') or item.filename.endswith('.ps1'):continue
            out=(root/'game'/item.filename).resolve()
            if not out.is_relative_to(root/'game'):raise ValueError('Unsafe archive path')
            out.parent.mkdir(parents=True,exist_ok=True)
            with z.open(item) as src,out.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
    repo=Path(__file__).resolve().parents[1]
    for rel in ('jogar.sh','source/controls.py','source/bin/gamescope'):
        shutil.copy2(repo/rel,root/rel);(root/rel).chmod(0o755)
    print('Installed:',root)
    print('Add jogar.sh as a non-Steam game; leave compatibility forcing disabled.')

if __name__=='__main__':main()
