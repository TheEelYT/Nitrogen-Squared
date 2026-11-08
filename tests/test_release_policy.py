"""Exercise actual workflow conditions against dev/main/other branch contexts."""
import ast
import json
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.load((ROOT/'.github/workflows'/name).read_text(),Loader=yaml.BaseLoader)


def enabled(expression,ref,event='push'):
    expression=expression.replace('github.ref',json.dumps(ref)).replace('github.event_name',json.dumps(event))
    expression=expression.replace('&&',' and ').replace('||',' or ')
    tree=ast.parse(expression,mode='eval')
    allowed=(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.Compare,ast.Eq,ast.Constant)
    if any(not isinstance(node,allowed) for node in ast.walk(tree)):
        raise AssertionError('Review the new workflow condition syntax')
    return eval(compile(tree,'<workflow condition>','eval'),{'__builtins__':{}})


class ReleasePolicyTests(unittest.TestCase):
    def test_dev_runs_checks_and_both_package_jobs(self):
        for name in ('source-checks.yml','windows-runtime.yml'):
            data=workflow(name)
            self.assertEqual(data['on']['push']['branches'],['dev'])
            self.assertNotIn('paths-ignore',data['on']['push']) # Results-only SHAs can qualify before promotion.
        data=workflow('windows-release.yml')
        self.assertEqual(set(data['on']['push']['branches']),{'dev','main'})
        for name in ('package','linux-package','distribute'):
            for ref in ('refs/heads/dev','refs/heads/main'):
                self.assertTrue(enabled(data['jobs'][name]['if'],ref))
            self.assertFalse(enabled(data['jobs'][name]['if'],'refs/heads/release/0.2.0'))

    def test_dev_can_upload_candidate_but_cannot_create_release_or_refs(self):
        data=workflow('windows-release.yml')
        steps=data['jobs']['distribute']['steps']
        writes=[s for s in steps if 'gh release create' in s.get('run','') or "api('POST','git/refs'" in s.get('run','')]
        self.assertEqual(len(writes),2)
        for step in writes:
            self.assertFalse(enabled(step['if'],'refs/heads/dev'))
            self.assertTrue(enabled(step['if'],'refs/heads/main'))
        candidate=next(s for s in steps if s.get('uses','').startswith('actions/upload-artifact'))
        self.assertTrue(enabled(candidate['if'],'refs/heads/dev'))
        self.assertFalse(enabled(candidate['if'],'refs/heads/main'))
        self.assertEqual(candidate['with']['retention-days'],'30')
        self.assertIn('SHA256SUMS.txt',candidate['with']['path'])
        self.assertNotIn('.sha256',candidate['with']['path'])
        self.assertNotIn('source.zip',candidate['with']['path'])

    def test_distribution_requires_both_packages_and_exact_commit_checks(self):
        job=workflow('windows-release.yml')['jobs']['distribute']
        self.assertEqual(set(job['needs']),{'package','linux-package'})
        gate=next(s for s in job['steps'] if 'head_sha=$GITHUB_SHA' in s.get('run',''))
        self.assertIn('Source checks',gate['run'])
        self.assertIn('Runtime and renderer checks',gate['run'])
        self.assertIn("r['conclusion']=='success'",gate['run'])
        self.assertLess(job['steps'].index(gate),next(i for i,s in enumerate(job['steps']) if s.get('uses','').startswith('actions/upload-artifact')))
