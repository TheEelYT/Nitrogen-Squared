from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from package_source import audit_staging, collect, validate_file, ROOT
from release_checksums import (ASSET_NAME, LINUX_ASSET_NAME, CHECKSUM_NAME,
                               REPOSITORY, checksum_for, write_checksums,
                               publication_asset_names, maintain_published_release)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_release_stage_rejects_extra_disc_or_capture(self):
        (self.root / "README.md").write_text("Source only")
        for name in ("disc.bin", "overlay_captures.json"):
            extra = self.root / name
            extra.write_bytes(b"unexpected")
            with self.assertRaisesRegex(ValueError, "release files"):
                audit_staging(self.root, {"README.md"})
            extra.unlink()

    def test_renamed_executable_is_rejected(self):
        (self.root / "notes.md").write_bytes(b"PS-X EXE" + bytes(2048))
        with self.assertRaises(ValueError):
            validate_file(self.root, "notes.md")

    def test_renamed_emitter_output_is_rejected(self):
        payload = "void " + "func_" + "80010000(CPUState* cpu) {}"
        (self.root / "notes.md").write_text(payload)
        with self.assertRaisesRegex(ValueError, "Generated game"):
            validate_file(self.root, "notes.md")

    def test_private_cache_cannot_be_allowlisted(self):
        (self.root / "cache").mkdir()
        (self.root / "cache/notes.md").write_text("private")
        with self.assertRaises(ValueError):
            validate_file(self.root, "cache/notes.md")

    def test_source_manifest_can_be_packaged(self):
        files = collect(ROOT)
        self.assertIn("README.md", files)
        self.assertIn("tools/n2o_disc.py", files)

    def test_parent_path_cannot_be_allowlisted(self):
        with self.assertRaises(ValueError):
            validate_file(self.root, "../outside.md")

    def test_combined_checksums_cover_both_archives_and_roundtrip(self):
        files=[]
        for name,data in [(ASSET_NAME,b'original Windows fixture'),(LINUX_ASSET_NAME,b'original Linux fixture')]:
            p=self.root/name;p.write_bytes(data);files.append(p)
        out=self.root/CHECKSUM_NAME;write_checksums(files,out)
        for p in files:self.assertEqual(checksum_for(out.read_bytes(),p.name),hashlib.sha256(p.read_bytes()).hexdigest())
        self.assertEqual(out.read_bytes().splitlines()[0].split()[-1],LINUX_ASSET_NAME.encode())
        with self.assertRaises(ValueError):write_checksums([files[0],files[0]],out)

    def test_checksum_manifest_rejects_ambiguity_paths_and_oversize(self):
        line=('a'*64+'  '+ASSET_NAME+'\n').encode()
        self.assertEqual(checksum_for(line.replace(b'  ',b' *').replace(b'\n',b'\r\n'),ASSET_NAME),'a'*64)
        for data in [line+line,line+line.replace(ASSET_NAME.encode(),ASSET_NAME.lower().encode()),
                     line.replace(ASSET_NAME.encode(),b'../'+ASSET_NAME.encode()),b'bad',b'x'*65537,
                     line.replace(ASSET_NAME.encode(),LINUX_ASSET_NAME.encode())]:
            with self.subTest(data=data[:80]),self.assertRaises(ValueError):checksum_for(data,ASSET_NAME)
        with self.assertRaises(ValueError):checksum_for(line+('b'*64+'  '+LINUX_ASSET_NAME+'\n').encode(),ASSET_NAME,False)

    def test_publication_layout_has_one_manifest_after_the_bridge(self):
        for version in ['0.1.0','0.1.1']:
            names=publication_asset_names(version);self.assertIn(ASSET_NAME+'.sha256',names)
            self.assertIn(CHECKSUM_NAME,names);self.assertNotIn('Nitrogen-Squared-source.zip',names)
        for version in ['0.2.0','0.2.1','0.3.0','1.0.0']:
            self.assertEqual(set(publication_asset_names(version)),{ASSET_NAME,LINUX_ASSET_NAME,CHECKSUM_NAME})
        with self.assertRaises(ValueError):publication_asset_names('../version')

    def test_published_cleanup_preserves_archives_and_is_idempotent(self):
        for mode in ['new','existing','wrong-tag','bad-package','bad-manifest']:
            with self.subTest(mode=mode):
                payload={ASSET_NAME:b'Windows ZIP fixture',LINUX_ASSET_NAME:b'Linux ZIP fixture'}
                for name in [ASSET_NAME,LINUX_ASSET_NAME]:
                    payload[name+'.sha256']=(hashlib.sha256(payload[name]).hexdigest()+'  '+name+'\n').encode()
                source='Nitrogen-Squared-source.zip';payload[source]=b'redundant source fixture'
                sums=''.join(hashlib.sha256(payload[n]).hexdigest()+'  '+n+'\n' for n in sorted([ASSET_NAME,LINUX_ASSET_NAME])).encode()
                if mode in ['existing','bad-manifest']:payload[CHECKSUM_NAME]=sums if mode=='existing' else b'changed'
                if mode=='existing':del payload[source]
                if mode=='bad-package':payload[ASSET_NAME+'.sha256']=('0'*64+'  '+ASSET_NAME+'\n').encode()
                body='Original release notes.\n'+('**Checksum transition:** existing\n' if mode=='existing' else '')
                assets=[dict(name=n,size=len(b),digest='sha256:'+hashlib.sha256(b).hexdigest()) for n,b in payload.items()]
                mutations=[]
                def gh(*args):
                    if args[0]=='api':
                        if '/git/ref/' in args[1]:return json.dumps({'object':{'sha':('b' if mode=='wrong-tag' else 'a')*40}})
                        return json.dumps(dict(draft=False,prerelease=False,assets=assets,body=body))
                    if args[1]=='download':
                        n=args[args.index('--pattern')+1];p=Path(args[args.index('--dir')+1])/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(payload[n]);return ''
                    mutations.append(args)
                    if args[1]=='upload':
                        self.assertEqual(Path(args[3]).name,CHECKSUM_NAME);self.assertEqual(Path(args[3]).read_bytes(),sums)
                    elif args[1]=='delete-asset':self.assertEqual(args[3],source)
                    elif args[1]=='edit':self.assertTrue(Path(args[args.index('--notes-file')+1]).read_text().startswith(body))
                    else:self.fail(str(args))
                    return ''
                with patch('release_checksums.gh',side_effect=gh):
                    if mode in ['wrong-tag','bad-package','bad-manifest']:
                        with self.assertRaises(ValueError):maintain_published_release('v0.1.0','a'*40,REPOSITORY)
                        self.assertFalse(mutations)
                    else:
                        result=maintain_published_release('v0.1.0','a'*40,REPOSITORY)
                        self.assertTrue(result['legacy_checksums_preserved'])
                        self.assertEqual([a[1] for a in mutations],['upload','delete-asset','edit'] if mode=='new' else [])


if __name__ == "__main__":
    unittest.main()
