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

# Apply the complete verified 1.5.7 update over the original site.
patch=root/'still-pwa-update.zip'
assert patch.is_file(), 'Upload still-pwa-update.zip together with restore_site.py'
assert hashlib.sha256(patch.read_bytes()).hexdigest()=='81bc189696954b78dccf713c38a62daa421c59d5412957d64de800fb8b0b13f7', 'Update package checksum mismatch'
with zipfile.ZipFile(patch) as z:
 assert z.testzip() is None
 for item in z.infolist():
  dest=(target/item.filename).resolve()
  assert dest.is_relative_to(target.resolve()), item.filename
  assert not stat.S_ISLNK(item.external_attr>>16)
 z.extractall(target)
content=(target/'offline-manifest.js').read_text(encoding='utf-8')
offline=json.loads(content.removeprefix('const OFFLINE_MANIFEST=').strip().removesuffix(';'))
assert offline['version']=='1.5.7-pwa.1'
for item in offline['files']:
 data=(target/item['path']).read_bytes()
 assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'], item['path']
assert (target/'search-history.js').is_file() and (target/'learning-time.js').is_file()
print('Verified 1.5.7: dynamic update checking feedback, search history, learning duration and precomputed Apple reading translations.')
