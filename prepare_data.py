"""Extract the selected TrimMask data packages into their documented locations."""
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
import argparse,json
ROOT=Path(__file__).resolve().parent
def safe(root,name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('Unsafe archive path')
    result=(root/name).resolve()
    if not result.is_relative_to(root.resolve()):raise ValueError('Archive path outside the package')
    return result
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unpack',action='store_true',help='Extract plotting inputs and engineering models')
    parser.add_argument('--runtime',action='store_true',help='Extract the complete runtime')
    parser.add_argument('--validation',action='store_true',help='Extract scientific controls and reference inputs')
    args=parser.parse_args();selected=[]
    if args.unpack:selected.extend((p,ROOT) for p in sorted((ROOT/'data').glob('*.zip')))
    if args.runtime:selected.extend((p,ROOT/'plugin/runtime_package') for p in sorted((ROOT/'plugin').glob('runtime_*.zip')))
    if args.validation:selected.extend((p,ROOT) for p in sorted((ROOT/'validation').glob('*.zip')))
    if not selected:parser.print_help();return
    count=0
    for archive,target in selected:
        with ZipFile(archive) as z:
            for entry in z.infolist():
                if entry.is_dir():continue
                path=safe(target,entry.filename);data=z.read(entry)
                if len(data)!=entry.file_size:raise ValueError('Incomplete archive member: '+entry.filename)
                if path.exists():
                    if not path.is_file() or path.read_bytes()!=data:raise ValueError('Refusing to overwrite changed file: '+str(path))
                else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
                count+=1
    if args.unpack:
        catalog=json.loads((ROOT/'PLOT_INPUT_CATALOG.json').read_text(encoding='utf-8'))
        if len(catalog['rows'])!=81 or not all(safe(ROOT,r['destination']).is_file() for r in catalog['rows']):raise ValueError('Incomplete plotting inputs')
    print('Extracted',count,'files. No simulation was executed.')
if __name__=='__main__':main()
