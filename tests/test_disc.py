import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from n2o_disc import DiscError, IsoReader, exe_header, inspect, parse_cue, prepare, seed_candidates


def fake_exe():
    # Hand-authored synthetic MIPS program, no commercial game content.
    data = bytearray(4096)
    data[:8] = b"PS-X EXE"
    for off, value in [(16, 0x80010000), (24, 0x80010000), (28, 12), (48, 0x801ffff0)]:
        struct.pack_into("<I", data, off, value)
    struct.pack_into("<III", data, 2048, 0x0c004002, 0, 0x03e00008)
    return bytes(data)


def record(name, lba, size):
    n = name.encode("ascii")
    length = 33 + len(n) + (len(n) % 2 == 0)
    r = bytearray(length)
    r[0] = length
    struct.pack_into("<I", r, 2, lba)
    struct.pack_into(">I", r, 6, lba)
    struct.pack_into("<I", r, 10, size)
    struct.pack_into(">I", r, 14, size)
    r[32] = len(n)
    r[33:33 + len(n)] = n
    return bytes(r)


def fixture(root):
    raw = bytearray(72 * 2352)
    for s in range(72):
        start = s * 2352
        raw[start:start + 12] = b"\0" + b"\xff" * 10 + b"\0"
        raw[start + 15] = 2

    def sector(lba, data):
        raw[lba * 2352 + 24:lba * 2352 + 24 + len(data)] = data

    pvd = bytearray(2048)
    pvd[:7] = b"\x01CD001\x01"
    pvd[40:72] = b"SYNTHETIC".ljust(32, b" ")
    struct.pack_into("<I", pvd, 158, 20)
    struct.pack_into("<I", pvd, 166, 2048)
    sector(16, pvd)
    cnf = b"BOOT = cdrom:\\MAIN.EXE;1\r\n"
    exe = fake_exe()
    sector(20, record("SYSTEM.CNF;1", 22, len(cnf)) + record("MAIN.EXE;1", 24, len(exe)))
    sector(22, cnf)
    sector(24, exe[:2048])
    sector(25, exe[2048:])
    bin_path = root / "synthetic.bin"
    bin_path.write_bytes(raw)
    cue = root / "synthetic.cue"
    cue.write_text('FILE "synthetic.bin" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n'
                   ' TRACK 02 AUDIO\n INDEX 00 00:00:60\n INDEX 01 00:00:62\n')
    _, tracks = parse_cue(cue)
    identity = dict(game_id="TEST", boot_exe="MAIN.EXE", bin_size=len(raw),
                    bin_sha256=hashlib.sha256(raw).hexdigest(),
                    tracks=[dict(number=t.number, kind=t.kind, start=t.start, pregap=t.pregap) for t in tracks],
                    executables=[dict(path="MAIN.EXE", size=len(exe), sha256=hashlib.sha256(exe).hexdigest())])
    return cue, identity


class DiscTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cue, self.identity = fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_import_checks_identity_and_keeps_bytes_outside_source(self):
        destination = self.root / "private/installation"
        result = prepare(self.cue, destination, self.identity)
        self.assertEqual(result["volume"], "SYNTHETIC")
        self.assertFalse(result["runtime_ready"])
        self.assertEqual((destination / "executables/MAIN.EXE").read_bytes(), fake_exe())
        manifest = json.loads((destination / "installation.json").read_text())
        self.assertEqual(manifest["cue"], str(self.cue.resolve()))
        self.assertFalse(list(destination.glob("*.bin")))

    def test_changed_audio_track_is_rejected_before_destination_created(self):
        path = self.root / "synthetic.bin"
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        out = self.root / "rejected"
        with self.assertRaisesRegex(DiscError, "digest"):
            prepare(self.cue, out, self.identity)
        self.assertFalse(out.exists())

    def test_missing_audio_track_is_rejected(self):
        text = self.cue.read_text().split(" TRACK 02")[0]
        self.cue.write_text(text)
        with self.assertRaisesRegex(DiscError, "layout"):
            inspect(self.cue, self.identity)

    def test_existing_installation_is_preserved(self):
        out = self.root / "installation"
        out.mkdir()
        (out / "save.txt").write_text("preserve me")
        with self.assertRaisesRegex(DiscError, "already exists"):
            prepare(self.cue, out, self.identity)
        self.assertEqual((out / "save.txt").read_text(), "preserve me")

    def test_failed_extraction_removes_staging(self):
        from unittest.mock import patch
        with patch("n2o_disc.seed_candidates", side_effect=[[], RuntimeError("simulated disk error")]):
            with self.assertRaises(RuntimeError):
                prepare(self.cue, self.root / "installation", self.identity)
        self.assertFalse((self.root / "installation").exists())
        self.assertEqual(list(self.root.glob(".n2o-import-*")), [])

    def test_path_traversal_rejected(self):
        for name in ["../synthetic.bin", "C:\\synthetic.bin", "\\\\host\\synthetic.bin"]:
            self.cue.write_text(f'FILE "{name}" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n')
            with self.assertRaises(DiscError):
                parse_cue(self.cue)

    def test_out_of_data_track_extent_is_rejected(self):
        with IsoReader(self.root / "synthetic.bin", 60) as iso:
            with self.assertRaisesRegex(DiscError, "exceeds"):
                iso.read(60, 2048)

    def test_header_rejects_truncation_and_invalid_addresses(self):
        data = bytearray(fake_exe())
        struct.pack_into("<I", data, 28, 0x200000)
        with self.assertRaises(DiscError):
            exe_header(data)
        data = bytearray(fake_exe())
        struct.pack_into("<I", data, 16, 0x80020000)
        with self.assertRaises(DiscError):
            exe_header(data)

    def test_jal_candidates_are_in_image_addresses(self):
        self.assertEqual(seed_candidates(fake_exe()), [0x80010000, 0x80010008])


if __name__ == "__main__":
    unittest.main()
