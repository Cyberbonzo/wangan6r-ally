from pathlib import Path
import zipfile,json,hashlib,shutil,sys
r=Path(sys.argv[1]).resolve()
p=r/'dependencias/english-patch.zip'
if not p.exists():p=r/'dependencias/WMMT6R English Patch.zip'
expected='edb2f140c3a302e89ae8eda4d1939b56a9ede61646ff396a6a9a5c338e53a89f'
assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==expected
report=[]
with zipfile.ZipFile(p) as z:
    bad=z.testzip();assert bad is None,bad
    for i in z.infolist():
        if i.is_dir():continue
        rel=Path(i.filename)
        assert rel.parts[0] in ('data','data_jp') and rel.suffix.lower() not in ('.exe','.dll','.bat','.ps1')
        dest=(r/'game'/rel).resolve()
        assert dest.is_relative_to((r/'game').resolve())
        backup=r/'backup-japones'/rel
        if dest.exists() and not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with z.open(i) as a,dest.open('wb') as b:shutil.copyfileobj(a,b)
        report.append({'path':i.filename,'sha256':hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()})
(r/'logs/english-patch.json').write_text(json.dumps({'author':'Tattoohanz','archive_sha256':expected,'files':report},indent=2))
print('English patch applied with backup:',len(report),'files')
