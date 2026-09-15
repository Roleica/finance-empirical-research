import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

p = Path(__file__).resolve().parents[1] / 'skills/finance-empirical-research/scripts/ledger.py'
spec = importlib.util.spec_from_file_location('ledger', p)
ledger = importlib.util.module_from_spec(spec); spec.loader.exec_module(ledger)


class Tests(unittest.TestCase):
    def audit(self, specs, results):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory)/'specs.jsonl',Path(directory)/'results.jsonl']
            for path, records in zip(paths,[specs,results]):
                path.write_text('\n'.join(json.dumps(r) for r in records))
            return ledger.audit(*paths)

    def test_success(self):
        self.assertTrue(self.audit([{'id':'a'}],[{'id':'a','status':'succeeded'}])['resolved_execution'])
    def test_not_applicable_requires_reason(self):
        self.assertFalse(self.audit([{'id':'a'}],[{'id':'a','status':'not_applicable'}])['resolved_execution'])
    def test_missing(self):
        self.assertEqual(self.audit([{'id':'a'}],[])['missing_results'],['a'])
    def test_duplicate(self):
        self.assertFalse(self.audit([{'id':'a'}],[{'id':'a','status':'succeeded'}]*2)['accounted'])
    def test_pending_failure_and_stale(self):
        for status in ['pending','running','failed','blocked','stale']:
            r=self.audit([{'id':'a'}],[{'id':'a','status':status}]); self.assertTrue(r['accounted']); self.assertFalse(r['resolved_execution'])
    def test_invalid(self):
        self.assertFalse(self.audit([{'id':'a'}],[{'id':'a','status':'done'}])['accounted'])
    def test_extra_and_missing_id(self):
        self.assertFalse(self.audit([{}],[{'id':'b','status':'succeeded'}])['accounted'])
    def test_empty_not_complete(self):
        self.assertFalse(self.audit([],[])['resolved_execution'])
    def test_explained_exclusion(self):
        self.assertTrue(self.audit([{'id':'a'}],[{'id':'a','status':'not_applicable','reason':'No temporal observations'}])['resolved_execution'])
    def test_query_bounds_and_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            records=Path(directory)/'records.jsonl'
            records.write_text('\n'.join(json.dumps({'id':str(i),'method':'中介','other':'x'}) for i in range(30)))
            result=subprocess.run([sys.executable,str(p),'query',str(records),'--query','中介','--fields','id,method'],capture_output=True,text=True,check=True)
            value=json.loads(result.stdout)
            self.assertEqual(value['returned'],20);self.assertTrue(value['truncated'])
            self.assertEqual(set(value['records'][0]),{'id','method'})
    def test_strict_json(self):
        with tempfile.TemporaryDirectory() as directory:
            records=Path(directory)/'bad.jsonl';records.write_text('{"value":NaN}')
            with self.assertRaises(ValueError): list(ledger.rows(records))
    def test_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'empty'; p.touch()
            self.assertEqual(ledger.digest(p),'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')


if __name__ == '__main__': unittest.main()
