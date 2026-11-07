#!/usr/bin/env python3
"""Bind original option enhancements to the player's verified USA executable."""
import hashlib
import json
from pathlib import Path
import struct
from n2o_disc import ROOT, exe_header


def prepare_options(installation: Path, output: Path) -> Path:
    expected = next(e for e in json.loads((ROOT/'configs/disc_usa.json').read_text())['executables']
                    if e['path'] == 'N2O.EXE')
    data = (installation/'executables/N2O.EXE').read_bytes()
    if len(data) != expected['size'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
        raise ValueError('Game options require the verified USA N2O.EXE')
    base = exe_header(data)['load_address']
    rows = []
    for address, end in [(0x8006761c, 0x8006c30c), (0x80066b58, 0x800674cc),
                         (0x80063114, 0x80063188), (0x8002aa54, 0x8002aed0)]:
        offset = 2048 + address-base
        body = data[offset:offset+end-address]
        if offset < 2048 or len(body) != end-address:
            raise ValueError('Game options binding is outside the verified executable')
        h = 14695981039346656037
        for byte in body:
            h = ((h ^ byte)*1099511628211) & ((1 << 64)-1)
        words = ','.join(f'0x{x:08x}u' for x in struct.unpack_from('<4I', body))
        rows.append(f'{{0x{address:08x}u,{len(body)}u,0x{h:016x}ull,'+'{'+words+'}}')
    text = ('// Private generated instruction guards. Do not distribute.\n'
            '#pragma once\n#include "options_contract.h"\nnamespace nitrogen::options {\n'
            'constexpr Binding binding{true,' + ','.join(rows) + '};\n}\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists() or output.read_text() != text:
        output.write_text(text, encoding='utf-8')
    return output
