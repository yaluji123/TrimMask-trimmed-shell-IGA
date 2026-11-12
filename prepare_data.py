"""Check this data release and optionally extract the selected input packages."""
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
import argparse,hashlib,json

ROOT=Path(__file__).resolve().parent
def digest(data):return hashlib.sha256(data).hexdigest()
def safe(root,name):
    rel=PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name:raise ValueError('Unsafe archive path: '+name)
    path=(root/name).resolve()
    if not path.is_relative_to(root.resolve()):raise ValueError('Path outside the package: '+name)
    return path
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unpack',action='store_true',help='Extract plotting inputs, caches and five engineering models')
    parser.add_argument('--runtime',action='store_true',help='Extract the complete runtime into plugin/runtime_package')
    parser.add_argument('--validation',action='store_true',help='Extract scientific validation data and reference input decks')
    args=parser.parse_args();index=json.loads((ROOT/'DATA_INDEX.json').read_text(encoding='utf-8'))
    for row in index['files']:
        data=safe(ROOT,row['file']).read_bytes()
        if len(data)!=row['bytes'] or digest(data)!=row['sha256']:raise ValueError('File identity mismatch: '+row['file'])
    refs={};selected=[]
    if args.unpack:selected.extend((p,ROOT) for p in sorted((ROOT/'data').glob('*.zip')))
    if args.runtime:selected.extend((p,ROOT/'plugin/runtime_package') for p in sorted((ROOT/'plugin').glob('runtime_*.zip')))
    if args.validation:selected.extend((p,ROOT) for p in sorted((ROOT/'validation').glob('*.zip')))
    for archive,target in selected:
        with ZipFile(archive) as z:
            for row in json.loads(z.read('MEMBERS.json')):
                path=safe(target,row['file']);data=z.read(row['file'])
                if len(data)!=row['bytes'] or digest(data)!=row['sha256']:raise ValueError('Archive member mismatch: '+row['file'])
                refs[(str(target),row['file'])]=row['sha256']
                if path.exists():
                    if not path.is_file() or digest(path.read_bytes())!=row['sha256']:raise ValueError('Refusing to overwrite changed file: '+str(path))
                else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    if args.unpack:
        catalog=json.loads((ROOT/'PLOT_INPUT_CATALOG.json').read_text(encoding='utf-8'))
        if len(catalog['rows'])!=83:raise ValueError('Unexpected plotting input catalog')
        for row in catalog['rows']:
            if refs.get((str(ROOT),row['destination']))!=row['sha256']:raise ValueError('Missing plotting input: '+row['destination'])
    print('Distributed file identities verified. Selected packages extracted without overwriting changed files.')
    print('No simulation or numerical validation was executed.')
if __name__=='__main__':main()
