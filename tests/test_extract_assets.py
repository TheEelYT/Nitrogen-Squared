"""Original disc/audio fixtures for private asset extraction; no game content."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from extract_assets import extract,plan_files
from n2o_disc import Entry,prepare
from portable_support import sha256
from test_disc import fixture,record


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.cue,self.identity=fixture(self.root)
        self.bin=self.root/"synthetic.bin"
        raw=bytearray(self.bin.read_bytes());cnf=b"BOOT = cdrom:\\MAIN.EXE;1\r\n"
        self.texture=b"original texture fixture"
        records=record("SYSTEM.CNF;1",22,len(cnf))+record("MAIN.EXE;1",24,4096)
        records+=record("SHIP.TIM;1",30,len(self.texture))+record("MOVIE.STR;1",40,4096)+record("TRACK.RAW;1",62,10*2048)
        raw[20*2352+24:20*2352+24+2048]=records.ljust(2048,b"\0")
        raw[30*2352+24:30*2352+24+len(self.texture)]=self.texture
        for lba in (40,41):
            raw[lba*2352+18]=raw[lba*2352+22]=0x28
            raw[lba*2352+24:lba*2352+32]=b"original"
        self.pcm=struct.pack("<hhhh",1,-1,32767,-32768)*(10*2352//8)
        raw[62*2352:]=self.pcm
        self.pregap=bytes(range(256))*(2*2352//256)+bytes(range((2*2352)%256))
        raw[60*2352:62*2352]=self.pregap
        self.bin.write_bytes(raw);self.raw=bytes(raw)
        self.identity["bin_sha256"]=hashlib.sha256(raw).hexdigest()
        self.installation=self.root/"installation"
        prepare(self.cue,self.installation,self.identity)
        self.output=self.root/"private/game"

    def tearDown(self):self.temp.cleanup()

    def test_assets_movies_music_and_audio_aliases_preserve_source_bytes(self):
        result=extract(self.installation,self.output,self.identity,lambda _:None)
        self.assertFalse(result["runtime_uses_catalog"])
        self.assertEqual((self.output/"assets/textures/SHIP.TIM").read_bytes(),self.texture)
        self.assertEqual((self.output/"movies/MOVIE.STR").read_bytes(),self.raw[40*2352:42*2352])
        with wave.open(str(self.output/"music/track-02.wav"),"rb") as wav:
            self.assertEqual((wav.getnchannels(),wav.getsampwidth(),wav.getframerate()),(2,2,44100))
            self.assertEqual(wav.getnframes(),10*588)
            self.assertEqual(wav.readframes(wav.getnframes()),self.pcm)
        self.assertEqual((self.output/"disc/pregaps/track-02.pcm").read_bytes(),self.pregap)
        alias=next(r for r in result["files"] if r["source"]=="TRACK.RAW")
        self.assertEqual(alias["representation"],"audio-track-alias")
        self.assertEqual(alias["output"],"music/track-02.wav")
        self.assertFalse((self.output/"system/TRACK.RAW").exists())
        for name,info in result["outputs"].items():
            self.assertEqual(info["size"],(self.output/name).stat().st_size)
            self.assertEqual(info["sha256"],sha256(self.output/name))
        self.assertEqual(json.loads((self.output/"asset-manifest.json").read_text()),result)
        self.assertEqual(self.bin.read_bytes(),self.raw)

    def test_existing_asset_edits_are_never_overwritten(self):
        self.output.mkdir(parents=True);(self.output/"valued-edit.txt").write_text("keep")
        with self.assertRaisesRegex(ValueError,"already exists"):
            extract(self.installation,self.output,self.identity,lambda _:None)
        self.assertEqual((self.output/"valued-edit.txt").read_text(),"keep")

    def test_mid_extraction_failure_removes_staging_only(self):
        with patch("extract_assets.raw_chunks",side_effect=OSError("original simulated write failure")):
            with self.assertRaises(OSError):extract(self.installation,self.output,self.identity,lambda _:None)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.output.parent.glob(".n2o-assets-*")))
        self.assertTrue((self.installation/"installation.json").is_file())

    def test_changed_audio_is_rejected_before_asset_destination_exists(self):
        raw=bytearray(self.raw);raw[-1]^=1;self.bin.write_bytes(raw)
        with self.assertRaises(ValueError):extract(self.installation,self.output,self.identity,lambda _:None)
        self.assertFalse(self.output.parent.exists())

    def test_unrecognized_alias_and_data_track_overrun_fail(self):
        tracks=self.identity["tracks"]
        for entry in (Entry("UNKNOWN.RAW",63,10*2048,False),Entry("BAD.TIM",59,4096,False)):
            with self.subTest(entry=entry),self.assertRaises(ValueError):plan_files([entry],tracks,72)

    def test_unsafe_or_duplicate_names_fail_before_writes(self):
        tracks=self.identity["tracks"]
        for entries in ([Entry("../OUT",30,4,False)],
                        [Entry("A.TIM",30,4,False),Entry("a.tim",31,4,False)]):
            with self.assertRaises(ValueError):plan_files(entries,tracks,72)


if __name__=="__main__":unittest.main()
