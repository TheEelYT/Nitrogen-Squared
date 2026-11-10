"""Build the GPL Tauri launcher and collect exact dependency notices. No game inputs."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from n2o_disc import ROOT


def build():
    frontend=ROOT/'launcher'
    env=os.environ.copy();env['CARGO_BUILD_JOBS']='2'
    env['N2_LAUNCHER_CHANNEL']='stable' if env.get('GITHUB_REF')=='refs/heads/main' else 'dev'
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    cargo=shutil.which('cargo')
    if not npm or not cargo: raise RuntimeError('Launcher builds need Node.js 24 and Rust stable. See launcher/README.md.')
    subprocess.run([npm,'ci','--ignore-scripts','--no-audit','--no-fund'],cwd=frontend,env=env,check=True)
    # Generate Windows .ico and native RGBA PNG from the exact owner-created logo.
    # The inputs remain separately hash-gated by package_source.launcher_assets.
    from package_source import launcher_assets
    launcher_assets(ROOT)
    from PIL import Image
    icons=frontend/'src-tauri/icons';icons.mkdir(exist_ok=True)
    with Image.open(frontend/'assets/logo.png') as source:
        image=source.convert('RGBA');image.thumbnail((256,256),Image.Resampling.LANCZOS)
        square=Image.new('RGBA',(256,256));square.alpha_composite(image,((256-image.width)//2,(256-image.height)//2))
        square.save(icons/'icon.png');square.save(icons/'icon.ico',sizes=[(32,32),(48,48),(64,64),(128,128),(256,256)])
    subprocess.run([npm,'run','tauri','--','build','--no-bundle','--ci','--','--locked'],cwd=frontend,env=env,check=True)
    binary=frontend/'src-tauri/target/release'/('nitrogen-launcher.exe' if os.name=='nt' else 'nitrogen-launcher')
    if not binary.is_file():raise RuntimeError('Tauri did not produce the launcher executable')
    output=ROOT/'dist'/('launcher-windows' if os.name=='nt' else 'launcher-linux')
    output.mkdir(parents=True,exist_ok=True)
    shutil.copy2(binary,output/('launcher.exe' if os.name=='nt' else 'launcher'))
    notices=output/'licenses'
    if notices.exists():shutil.rmtree(notices)
    notices.mkdir()
    # Metadata gives resolved sources for both runtime and build dependencies.
    # Copy all advertised license files, rather than substituting a generic SPDX label.
    metadata=json.loads(subprocess.check_output([cargo,'metadata','--locked','--format-version','1'],cwd=frontend/'src-tauri',env=env))
    index=[]
    for package in metadata['packages']:
        if package['source'] is None:continue
        directory=Path(package['manifest_path']).parent
        target=notices/(package['name']+'-'+package['version'])
        candidates=[p for p in directory.iterdir() if p.is_file() and p.name.upper().startswith(('LICENSE','LICENCE','COPYING','NOTICE','UNLICENSE'))]
        if package.get('license_file'):
            path=directory/package['license_file']
            if path.is_file() and path not in candidates:candidates.append(path)
        if candidates:
            target.mkdir()
            for path in candidates:shutil.copy2(path,target/path.name)
        index.append(dict(name=package['name'],version=package['version'],license=package.get('license'),repository=package.get('repository'),files=[str(p.relative_to(directory)) for p in candidates]))
    (notices/'DEPENDENCIES.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    print('TAURI_LAUNCHER_BUILT',binary,flush=True)
    return output

if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args();build()
