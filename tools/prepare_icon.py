#!/usr/bin/env python3
"""Decode the player's verified save icon into PRIVATE PNG/ICO build inputs.

No palette, pixels or other commercial bytes are embedded here. Standard library
only; generated files belong under .local and must never enter public packages.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import zlib

from n2o_disc import ROOT, default_data_dir


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_icon(palette: bytes, packed: bytes) -> bytes:
    """One 16x16 PS1 icon, low nibble first; zero CLUT words are transparent."""
    if len(palette) != 32 or len(packed) != 128:
        raise ValueError("Expected a 16-colour palette and 16x16 packed icon")
    colours=[]
    for colour in struct.unpack('<16H', palette):
        colours.append(bytes([*(((colour >> shift & 31)*255+15)//31 for shift in (0,5,10)),
                              0 if colour == 0 else 255]))
    return b''.join(colours[index] for value in packed for index in (value & 15, value >> 4))


def scaled_rgba(pixels: bytes, size: int) -> bytes:
    if len(pixels) != 16*16*4 or size not in (16,32,48,64,128,256):
        raise ValueError("Unsupported private icon dimensions")
    return b''.join(pixels[((y*16//size)*16+x*16//size)*4:((y*16//size)*16+x*16//size)*4+4]
                    for y in range(size) for x in range(size))


def png_bytes(pixels: bytes, size=256) -> bytes:
    rgba=scaled_rgba(pixels,size)
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    rows=b''.join(b'\0'+rgba[y*size*4:(y+1)*size*4] for y in range(size))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',size,size,8,6,0,0,0))+
            chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b''))


def ico_bytes(pixels: bytes) -> bytes:
    sizes=(16,32,48,64,128,256);images=[];entries=[];offset=6+16*len(sizes)
    for size in sizes:
        rgba=scaled_rgba(pixels,size);xor=bytearray();mask=bytearray()
        for y in range(size-1,-1,-1):
            row=bytearray(((size+31)//32)*4)
            for x in range(size):
                r,g,b,a=rgba[(y*size+x)*4:(y*size+x)*4+4]
                xor.extend((b,g,r,a))
                if not a:row[x//8] |= 0x80 >> (x%8)
            mask.extend(row)
        dib=struct.pack('<IiiHHIIiiII',40,size,size*2,1,32,0,len(xor)+len(mask),0,0,0,0)+xor+mask
        entries.append(struct.pack('<4B2H2I',size%256,size%256,0,0,1,32,len(dib),offset))
        images.append(dib);offset+=len(dib)
    return struct.pack('<3H',0,1,len(sizes))+b''.join(entries)+b''.join(images)


def _write(path: Path, data: bytes):
    if path.is_file() and path.read_bytes()==data:
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as temporary:
        temporary.write(data);name=Path(temporary.name)
    try:os.replace(name,path)
    finally:name.unlink(missing_ok=True)


def write_icons(pixels: bytes, output: Path) -> Path:
    output=output.resolve()
    if '.local' not in output.parts:
        raise ValueError("Derived game icons must stay in a private .local folder")
    _write(output/'psxrecomp.png',png_bytes(pixels))
    _write(output/'psxrecomp.ico',ico_bytes(pixels))
    return output/'psxrecomp.ico'


def prepare_icon(installation: Path, output: Path) -> Path:
    recipe=json.loads((ROOT/'configs/game_icon_usa.json').read_text(encoding='utf-8'))
    if (recipe.get('schema')!=1 or recipe.get('source')!='N2O.EXE' or
            recipe.get('format')!='ps1-clut16-icon-4bpp' or
            (recipe.get('width'),recipe.get('height'))!=(16,16)):
        raise ValueError('Unsupported private game icon recipe')
    identity=json.loads((ROOT/'configs/disc_usa.json').read_text(encoding='utf-8'))
    expected=next(row for row in identity['executables'] if row['path']==recipe['source'])
    data=(installation/'executables'/recipe['source']).read_bytes()
    if len(data)!=expected['size'] or digest(data)!=expected['sha256']:
        raise ValueError('Game icon requires the verified USA N2O.EXE; existing files were preserved')
    blocks=[]
    for name,length in [('palette',32),('pixels',128)]:
        offset=recipe.get(name+'_offset')
        if type(offset) is not int or offset<0 or offset+length>len(data):
            raise ValueError('Game icon extent is outside the verified executable')
        block=data[offset:offset+length]
        if digest(block)!=recipe.get(name+'_sha256'):
            raise ValueError('Verified game icon extent does not match its recipe')
        blocks.append(block)
    icon=write_icons(decode_icon(*blocks),output)
    receipt=dict(schema=1,kind='private-disc-derived-game-icon',public_distribution_allowed=False,
                 source=recipe['source'],source_sha256=expected['sha256'],
                 palette_sha256=recipe['palette_sha256'],pixels_sha256=recipe['pixels_sha256'],
                 outputs={p.name:dict(size=p.stat().st_size,sha256=digest(p.read_bytes()))
                          for p in (icon,icon.with_suffix('.png'))})
    _write(icon.parent/'icon.json',(json.dumps(receipt,indent=2)+'\n').encode('utf-8'))
    return icon


def verify_embedded_icon(executable: Path, icon: Path):
    """On Windows, compare every PE icon resource with the private ICO input."""
    if os.name != 'nt':
        raise RuntimeError('Embedded Windows icon verification requires Windows')
    import ctypes
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.LoadLibraryExW.argtypes=[wintypes.LPCWSTR,wintypes.HANDLE,wintypes.DWORD]
    kernel.LoadLibraryExW.restype=wintypes.HMODULE
    kernel.FindResourceW.argtypes=[wintypes.HMODULE,ctypes.c_void_p,ctypes.c_void_p]
    kernel.FindResourceW.restype=wintypes.HRSRC
    kernel.SizeofResource.argtypes=[wintypes.HMODULE,wintypes.HRSRC]
    kernel.SizeofResource.restype=wintypes.DWORD
    kernel.LoadResource.argtypes=[wintypes.HMODULE,wintypes.HRSRC]
    kernel.LoadResource.restype=wintypes.HGLOBAL
    kernel.LockResource.argtypes=[wintypes.HGLOBAL]
    kernel.LockResource.restype=ctypes.c_void_p
    kernel.FreeLibrary.argtypes=[wintypes.HMODULE]
    kernel.FreeLibrary.restype=wintypes.BOOL
    module=kernel.LoadLibraryExW(str(executable.resolve()),None,2)  # Data only: do not execute game code.
    if not module:raise RuntimeError('Cannot inspect the private executable icon resources')
    def resource(name,kind):
        ident=ctypes.cast(ctypes.c_wchar_p(name),ctypes.c_void_p) if isinstance(name,str) else ctypes.c_void_p(name)
        found=kernel.FindResourceW(module,ident,ctypes.c_void_p(kind))
        size=kernel.SizeofResource(module,found) if found else 0
        handle=kernel.LoadResource(module,found) if found else None
        pointer=kernel.LockResource(handle) if handle else None
        if not pointer or not 0<size<2*1024*1024:
            raise RuntimeError('The compiled game is missing its expected icon resource')
        return ctypes.string_at(pointer,size)
    try:
        expected=icon.read_bytes();group=resource('IDI_ICON1',14)
        header=struct.unpack_from('<3H',expected)
        if len(group)<6 or struct.unpack_from('<3H',group)!=header or len(group)!=6+14*header[2]:
            raise RuntimeError('The compiled game icon directory differs from its private input')
        for index in range(header[2]):
            entry=struct.unpack_from('<4B2H2I',expected,6+16*index)
            actual=struct.unpack_from('<4B2HIH',group,6+14*index)
            if entry[:7]!=actual[:7] or resource(actual[7],3)!=expected[entry[7]:entry[7]+entry[6]]:
                raise RuntimeError('The compiled game icon pixels differ from their private input')
    finally:
        kernel.FreeLibrary(module)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installation',type=Path,default=default_data_dir()/'SLUS-00637')
    parser.add_argument('--output',type=Path,default=ROOT/'.local/runtime-dev/private/game-icon')
    args=parser.parse_args()
    print(prepare_icon(args.installation,args.output))


if __name__=='__main__':main()
