"""Package reviewed launcher/source only; the player's Linux game is built locally."""
from pathlib import Path
import argparse
import tempfile
import zipfile
from n2o_disc import ROOT
from package_source import collect,audit_staging
from portable_support import LINUX_ASSET_NAME,extract_zip,sha256,write_json
from portable_update import verify_package,owned_path

FIRST_RUN='''Nitrogen Squared — Linux x86_64

Extract the complete Nitrogen-Squared folder somewhere writable, then run:
    sh launcher.sh
Select your USA CUE sheet with its matching BIN beside it. The launcher verifies,
imports, generates and compiles your private game, then starts it. Preparation
needs internet access; all downloaded/generated files and saves stay in .local.
Use Check for updates; keep .local and the original disc available.

Requires a graphical Linux x86_64 desktop, Python 3.11+ with Tk, Git, CMake 3.20+,
Make, a C11/C++17 compiler, pkg-config and OpenGL/EGL/X11/audio development files.
On Ubuntu 24.04 or newer, install prerequisites once:
    sudo apt install python3 python3-tk git cmake build-essential pkg-config libgl-dev libegl-dev libx11-dev libxcursor-dev libxi-dev libxrandr-dev libxfixes-dev libxext-dev libxss-dev libxtst-dev libxkbcommon-dev libudev-dev libusb-1.0-0-dev libdbus-1-dev libasound2-dev libpulse-dev xdg-utils
Other distributions need the equivalent packages. No sudo is used by the launcher.
The system Python and compiler are used; pinned SDL/framework source downloads
and all project state remain inside this folder. This is a source launcher
package, not an AppImage. No commercial data or prepared game binary is bundled.
See app/THIRD_PARTY.md for dependency notices. Very small windows retain 2x UI.
'''
LAUNCHER='''#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 -X utf8 -E -s -B "$root/app/tools/portable_launcher.py" --root "$root" "$@"
'''

def stage(output):
    files=collect(ROOT);output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nitrogen-linux-',dir=output.parent) as t:
        root=Path(t)/'Nitrogen-Squared';app=root/'app';app.mkdir(parents=True)
        for n,data in files.items():
            p=app/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        audit_staging(app,set(files))
        (root/'launcher.sh').write_text(LAUNCHER,encoding='utf-8',newline='\n');(root/'launcher.sh').chmod(0o755)
        (root/'README-FIRST.txt').write_text(FIRST_RUN,encoding='utf-8')
        inventory={}
        for p in sorted(root.rglob('*')):
            if p.is_file():
                n=p.relative_to(root).as_posix();owned_path(n);inventory[n]=dict(size=p.stat().st_size,sha256=sha256(p))
        write_json(root/'release-manifest.json',dict(schema=1,platform='linux-x86_64',version=(ROOT/'VERSION').read_text().strip(),files=inventory))
        verify_package(root)
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(root.rglob('*')):
                if p.is_file():z.write(p,'Nitrogen-Squared/'+p.relative_to(root).as_posix())
        extract_zip(output,Path(t)/'check');verify_package(Path(t)/'check/Nitrogen-Squared')
    output.with_name(output.name+'.sha256').write_text(sha256(output)+'  '+output.name+'\n',encoding='ascii')
    print('LINUX_PACKAGE_PASS',len(inventory),'owned files',sha256(output),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'dist'/LINUX_ASSET_NAME);stage(p.parse_args().output.resolve())
