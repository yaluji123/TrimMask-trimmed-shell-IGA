"""Verify the release and optionally unpack exact plotting inputs and CAD models."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import argparse, hashlib, json

ROOT=Path(__file__).resolve().parent
def digest(data):return hashlib.sha256(data).hexdigest()
def safe(root,name):
    relative=PurePosixPath(name)
    assert not relative.is_absolute() and '..' not in relative.parts and '\\' not in name
    path=(root/name).resolve();assert path.is_relative_to(root.resolve())
    return path
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unpack',action='store_true',help='Extract plotting inputs/caches and five CAD models into this repository')
    parser.add_argument('--runtime',action='store_true',help='Also extract the unchanged plugin into plugin/runtime_package')
    args=parser.parse_args()
    index=json.loads((ROOT/'DATA_INDEX.json').read_text(encoding='utf-8'))
    for row in index['files']:
        data=safe(ROOT,row['file']).read_bytes();assert len(data)==row['bytes'] and digest(data)==row['sha256'],row['file']
    refs={}
    for archive in sorted((ROOT/'data').glob('*.zip')):
        with ZipFile(archive) as z:
            members=json.loads(z.read('MEMBERS.json'))
            for row in members:
                data=z.read(row['file']);assert len(data)==row['bytes'] and digest(data)==row['sha256']
                refs[row['file']]=row['sha256']
                path=safe(ROOT,row['file'])
                if args.unpack:
                    if path.exists():assert digest(path.read_bytes())==row['sha256'],'Refusing to overwrite changed input: '+row['file']
                    else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    catalog=json.loads((ROOT/'PLOT_INPUT_CATALOG.json').read_text(encoding='utf-8'))
    assert len(catalog['rows'])==83
    for row in catalog['rows']:assert refs[row['destination']]==row['sha256']
    if args.runtime:
        archives=sorted((ROOT/'plugin').glob('runtime_*.zip'));assert archives
        for archive in archives:
            with ZipFile(archive) as z:
                for name in z.namelist():
                    if name=='MEMBERS.json':continue
                    path=safe(ROOT/'plugin/runtime_package',name);data=z.read(name)
                    if path.exists():assert digest(path.read_bytes())==digest(data),'Refusing to overwrite changed runtime: '+name
                    else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print('File identities verified. All83 plot inputs and five CAD models are present in the release.')
    print('Inputs unpacked.' if args.unpack else 'Run with --unpack for plotting inputs and CAD models.')
    print('No simulation or numerical validation was run.')
if __name__=='__main__':main()
