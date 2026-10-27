from pathlib import Path
import hashlib,json,zipfile,stat
root=Path(__file__).resolve().parent
manifest=json.loads((root/'still-site-manifest.json').read_text(encoding='utf-8'))
archive=root/'still-site-restored.zip'
with archive.open('wb') as output:
 for item in manifest['parts']:
  part=root/item['name']
  assert part.parent==root and part.is_file(),part.name
  data=part.read_bytes()
  assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],part.name
  output.write(data)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archiveSHA256']
target=root/'_site'
target.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for item in z.infolist():
  dest=(target/item.filename).resolve()
  assert dest.is_relative_to(target.resolve()),item.filename
  assert not stat.S_ISLNK(item.external_attr>>16)
 z.extractall(target)
assert (target/'index.html').is_file() and (target/'sw.js').is_file()
assert (target/'still.mobileconfig').is_file()
print('Verified and restored all offline application files.')

# 完整验证 iPhone 1.5.9 更新包
patch=root/'still-pwa-update.zip'
assert hashlib.sha256(patch.read_bytes()).hexdigest()=='f9eff8922b307fcae9d3cc74a4df020967d9f091b61f8050f2d18d2d7deb1eb7', '更新包校验失败'
with zipfile.ZipFile(patch) as z:
 assert z.testzip() is None
 for item in z.infolist():
  dest=(target/item.filename).resolve()
  assert dest.is_relative_to(target.resolve()), item.filename
 z.extractall(target)
content=(target/'offline-manifest.js').read_text(encoding='utf-8')
offline=json.loads(content.removeprefix('const OFFLINE_MANIFEST=').strip().removesuffix(';'))
assert offline['version']=='1.5.9-pwa.1'
for item in offline['files']:
 data=(target/item['path']).read_bytes()
 assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'], item['path']
assert (target/'chinese-index.json').is_file()
assert (target/'phrase-core.js').is_file()
print('Verified 1.5.9: full Chinese lookup index and reading phrase lookup included.')
