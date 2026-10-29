"""Synthetic code/data evidence tests; classifications never imply qualification."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from code_inventory import classify,fnv,intersect,merge,propose,subtract,trace_entries


class InventoryTests(unittest.TestCase):
    def test_partition_retains_unknowns_and_conflicting_hints(self):
        payload=b'ABCDEFGH\0'+bytes(55)
        analysis={'functions':[dict(addr=0x1000,end=0x1010,confidence='high',partial=False,is_data=False)]}
        rows=classify(payload,0x1000,[(0x1000,0x1004)],analysis)
        self.assertEqual(rows['linked_translation']['bytes'],4)
        self.assertEqual(rows['conflicting_hints']['bytes'],5)
        self.assertEqual(rows['static_code_hint']['bytes'],7)
        self.assertEqual(rows['data_hint']['bytes'],0)
        self.assertEqual(rows['unclassified']['bytes'],48)
        self.assertEqual(sum(x['bytes'] for x in rows.values()),64)

    def test_data_is_a_hint_and_static_low_confidence_stays_unknown(self):
        payload=b'original text\0'+bytes(18)
        analysis={'functions':[dict(addr=0x2000,end=0x2020,confidence='low',partial=False,is_data=False)]}
        rows=classify(payload,0x2000,[],analysis)
        self.assertEqual(rows['static_code_hint']['bytes'],0)
        self.assertEqual(rows['data_hint']['bytes'],14)
        self.assertEqual(rows['unclassified']['bytes'],18)

    def test_invalid_ranges_are_rejected_and_unions_do_not_double_count(self):
        self.assertEqual(merge([(0,8),(4,12),(12,16)]),[(0,16)])
        self.assertEqual(subtract([(0,16)],[(3,5),(8,20)]),[(0,3),(5,8)])
        self.assertEqual(intersect([(0,10)],[(5,15)]),[(5,10)])
        with self.assertRaises(ValueError):classify(bytes(16),0x1000,[(0x1000,0x1014)],{})
        with self.assertRaises(ValueError):classify(bytes(16),0x1000,[],{'functions':[dict(addr=0x1000,end=0x1020)]})

    def test_trace_matching_keeps_overlapping_images_separate_and_never_claims_identity(self):
        images={'ONE':dict(base=0x80010000,payload=bytes(range(64))),
                'TWO':dict(base=0x80010000,payload=bytes(reversed(range(64))))}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace.tsv'
            p.write_text(f'0 80010000 {fnv(images["ONE"]["payload"][:32]):016X} 10\n')
            hits=trace_entries([p],images)
            self.assertEqual(hits['ONE'],{0x80010000});self.assertEqual(hits['TWO'],set())
            p.write_text('malformed\n')
            with self.assertRaises(ValueError):trace_entries([p],images)

    def test_whole_excluded_owner_blocks_discovered_internal_entries(self):
        base=0x80024000
        images={'NEW.EXE':dict(base=base,payload=bytes(256))}
        observed={'NEW.EXE':{base+16,base+128}}
        excluded=[dict(executable='NEW.EXE',start=f'0x{base:08X}',size=64)]
        roots=propose(images,{'NEW.EXE':[]},{},observed,excluded)
        self.assertEqual([r['start'] for r in roots],[f'0x{base+128:08X}'])
        self.assertNotIn('bytes_b64',json.dumps(roots))

    def test_candidate_extent_stops_before_linked_and_excluded_ranges(self):
        base=0x80030000
        images={'N2O.EXE':dict(base=base,payload=bytes(256))}
        observed={'N2O.EXE':{base}}
        roots=propose(images,{'N2O.EXE':[(base+64,base+80)]},{},observed,
                      [dict(executable='N2O.EXE',start=f'0x{base+128:08X}',size=32)])
        self.assertEqual(roots[0]['size'],64)


if __name__=='__main__':unittest.main()
