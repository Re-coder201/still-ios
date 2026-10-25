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
