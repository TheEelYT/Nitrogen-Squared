import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import prepare_media as media


class MediaBindingTests(unittest.TestCase):
    def fixture(self, root):
        (root/'executables').mkdir();(root/'configs').mkdir()
        data=bytearray(2048+16384);data[:8]=b'PS-X EXE'
        for offset,value in [(16,0x80020000),(24,0x80020000),(28,16384),(48,0x801fff00)]:struct.pack_into('<I',data,offset,value)
        (root/'executables/NEW.EXE').write_bytes(data)
        identity={'executables':[{'path':'NEW.EXE','size':len(data),'sha256':hashlib.sha256(data).hexdigest()}]}
        (root/'configs/disc_usa.json').write_text(json.dumps(identity))
        return {'bin':str(root/'private-disc.bin'),'tracks':[{}, {'pregap':1234,'start':1236}]}

    def test_private_binding_is_portable_and_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);manifest=self.fixture(root);output=root/'private/binding.h'
            reader=SimpleNamespace(__enter__=None)
            names=['FOX.SXA','N2O.SXA','N2OEND.SXA','CRYSTAL.SXA']
            with patch.object(media,'ROOT',root),patch.object(media,'IsoReader') as iso:
                iso.return_value.__enter__.return_value.inventory.return_value=(None,[SimpleNamespace(path=n,lba=i*10+1,size=4096) for i,n in enumerate(names)])
                media.prepare_media(manifest,root,output);text=output.read_text();stamp=output.stat().st_mtime_ns
                media.prepare_media(manifest,root,output)
                self.assertEqual(stamp,output.stat().st_mtime_ns)
                self.assertNotIn(str(root),text);self.assertIn('824u',text);self.assertIn('0x80022350u',text)
                for n in names:self.assertIn(n,text)
                iso.assert_called_with(Path(manifest['bin']),1234)

    def test_changed_executable_never_writes_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);manifest=self.fixture(root);(root/'executables/NEW.EXE').write_bytes(b'changed')
            with patch.object(media,'ROOT',root),self.assertRaises(ValueError):media.prepare_media(manifest,root,root/'private/binding.h')
            self.assertFalse((root/'private').exists())
