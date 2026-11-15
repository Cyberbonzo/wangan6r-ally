#!/usr/bin/env python3
"""Apply private, user-supplied artwork through the running Steam client."""
import argparse
import base64
import hashlib
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from steam_cdp import SteamCDP

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.home()/'Games/Wangan6R')
    parser.add_argument('--app-id',type=int,required=True)
    parser.add_argument('--account',required=True,help='Steam userdata directory name')
    args=parser.parse_args()
    if not args.account.isdigit() or not 0<args.app_id<2**32:
        parser.error('Invalid Steam identifiers')
    root=args.root.expanduser().resolve();art=root/'artes'
    grid=Path.home()/'.local/share/Steam/userdata'/args.account/'config/grid'
    assert grid.is_dir(),'Steam grid directory not found'
    assets=[('portrait.png',0,'p'),('hero.png',1,'_hero'),
            ('logo.png',2,'_logo'),('landscape.png',3,''),('icon.png',4,'_icon')]
    for filename,_,_ in assets:
        path=art/filename
        assert path.is_file() and path.stat().st_size<20_000_000,filename
        data=path.read_bytes()
        assert (data.startswith(b'\x89PNG\r\n\x1a\n') if path.suffix=='.png' else data.startswith(b'\xff\xd8')),filename
    backup=root/'source/artwork-backup'/datetime.now().strftime('%Y%m%d-%H%M%S')
    backup.mkdir(parents=True,exist_ok=False)
    for p in grid.glob(str(args.app_id)+'*'):
        if p.is_file():shutil.copy2(p,backup/p.name)
    c=SteamCDP()
    name=c.evaluate(f'appStore.GetAppOverviewByAppID({args.app_id})?.display_name')
    assert name=='Wangan Midnight Maximum Tune 6R',f'Unexpected shortcut: {name!r}'
    report={'app_id':args.app_id,'name':name,'assets':[]}
    for filename,kind,suffix in assets:
        src=art/filename;ext=src.suffix[1:]
        dest=grid/(str(args.app_id)+suffix+'.'+ext)
        if kind==4:
            # Non-Steam icons use the shortcut API; artwork type 4 can reject them.
            shutil.copy2(src,dest)
            c.evaluate('SteamClient.Apps.SetShortcutIcon('+str(args.app_id)+','+json.dumps(str(src))+')')
        else:
            c.evaluate(f'SteamClient.Apps.ClearCustomArtworkForApp({args.app_id},{kind})')
            time.sleep(.6)
            payload=base64.b64encode(src.read_bytes()).decode()
            c.evaluate('SteamClient.Apps.SetCustomArtworkForApp('+','.join(map(json.dumps,[args.app_id,payload,ext,kind]))+')')
        for _ in range(30):
            if dest.is_file() and digest(dest)==digest(src):break
            time.sleep(.1)
        assert dest.is_file() and digest(dest)==digest(src),f'Artwork not persisted: {filename}'
        report['assets'].append({'source':filename,'steam_file':dest.name,'sha256':digest(src),'verified':True})
        print('Installed and verified:',filename,flush=True)
    c.evaluate('SteamClient.Apps.SetShortcutIcon('+str(args.app_id)+','+json.dumps(str(art/'icon.png'))+')')
    report['overview']=c.evaluate(f'({{custom_images_found:appStore.GetAppOverviewByAppID({args.app_id}).custom_images_found}})')
    (root/'logs').mkdir(exist_ok=True)
    (root/'logs/artwork-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('All five artwork files verified.')

if __name__=='__main__':main()
