"""Windows-only original integration fixture for copied-process self-updates."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from portable_support import Layout,sha256,write_json
from portable_update import read_manifest,verify_package


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    args=p.parse_args()
    if os.name!='nt':raise RuntimeError('Windows integration fixture only')
    layout=Layout(args.root)
    old=read_manifest(layout.root)
    stage=layout.local/'updates/integration-package/Nitrogen-Squared'
    if stage.exists():raise ValueError('Use a fresh extracted package for the integration fixture')
    stage.mkdir(parents=True)
    for name in old['files']:
        path=stage/name;path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(layout.root/name,path)
    numbers=list(map(int,old['version'].split('.')));numbers[-1]+=1
    new_version='.'.join(map(str,numbers))
    (stage/'app/VERSION').write_text(new_version+'\n')
    new=dict(old,version=new_version,files={name:dict(size=(stage/name).stat().st_size,sha256=sha256(stage/name)) for name in old['files']})
    write_json(stage/'release-manifest.json',new)
    verify_package(stage)
    sentinels={'.local/saves/original-fixture.txt':b'original save preservation fixture',
               '.local/runtime-dev/original-fixture.txt':b'original cache preservation fixture'}
    for name,data in sentinels.items():
        path=layout.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    report=layout.local/'updated-launcher-smoke.json'
    # This parent releases the old interpreter before the copied runner installs.
    script='import sys; sys.path.insert(0,'+repr(str(layout.app/'tools'))+'); from pathlib import Path; from portable_support import Layout; from portable_update import start_updater; start_updater(Layout(Path('+repr(str(layout.root))+')),Path('+repr(str(stage))+'),0,restart_report=Path('+repr(str(report))+'))'
    env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
    command=[str(layout.python),'-E','-s','-B','-c',script]
    subprocess.run(command,env=env,cwd=layout.root,check=True,timeout=60)
    deadline=time.monotonic()+120
    while time.monotonic()<deadline and not report.exists():time.sleep(.25)
    if not report.exists():
        log=layout.local/'update.log'
        raise RuntimeError('Copied updater did not restart successfully:\n'+(log.read_text(errors='replace') if log.exists() else 'No update log'))
    result=json.loads(report.read_text())
    if result['version']!=new_version or read_manifest(layout.root)['version']!=new_version:
        raise RuntimeError('Updated launcher did not load the new source version')
    for name,data in sentinels.items():
        if (layout.root/name).read_bytes()!=data:raise RuntimeError('Update changed private data')
    if (layout.local/'update-state.json').exists():raise RuntimeError('Update transaction did not finish')
    print('PORTABLE_SELF_UPDATE_PASS: actual bundled Python/Win32 restart, new version loaded, private cache and saves preserved',flush=True)


if __name__=='__main__':main()
