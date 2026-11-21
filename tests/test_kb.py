import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import kb
import check_urls


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'schemas').mkdir()
        shutil.copy(kb.ROOT/'schemas/entry.schema.json', self.root/'schemas/entry.schema.json')
        for file in ['projects/liteeth.yaml','projects/litex.yaml',
                     'catalog/ethernet/liteeth-ecp5-rgmii.yaml']:
            target=self.root/file;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy(kb.ROOT/file,target)
        self.core_path=self.root/'catalog/ethernet/liteeth-ecp5-rgmii.yaml'
        self.core=yaml.safe_load(self.core_path.read_text())

    def write_core(self):
        self.core_path.write_text(yaml.safe_dump(self.core))

    def test_valid_seed(self):
        self.assertEqual(kb.validate(self.root),[])

    def test_yaml_duplicate_keys_rejected(self):
        self.core_path.write_text(self.core_path.read_text()+'\nid: duplicate\n')
        with self.assertRaisesRegex(ValueError,'duplicate YAML key'):
            kb.load(self.root)

    def test_unknown_field_and_bad_date_rejected(self):
        self.core['reviewed_at']='2026-99-40'
        self.core['quality_score']=100
        self.write_core()
        self.assertTrue(kb.validate(self.root))

    def test_non_unknown_fact_requires_evidence(self):
        self.core['verification']['synthesis']['status']='passed'
        self.write_core()
        self.assertTrue(kb.validate(self.root))

    def test_readme_cannot_establish_pass(self):
        fact=self.core['verification']['synthesis']
        fact['status']='passed';fact['evidence']=self.core['verification']['source']['evidence']
        self.write_core()
        self.assertTrue(any('result requires' in e for e in kb.validate(self.root)))

    def test_simulation_does_not_establish_synthesis(self):
        ev=dict(self.core['verification']['source']['evidence'][0],type='our_simulation',
                toolchain='test simulator',report='reports/run.txt')
        (self.root/'reports').mkdir();(self.root/'reports/run.txt').write_text('fixture')
        self.core['verification']['synthesis'].update(status='passed',evidence=[ev])
        self.write_core()
        self.assertTrue(any('does not establish synthesis' in e for e in kb.validate(self.root)))

    def test_lifecycle_requires_our_result(self):
        self.core['lifecycle']='hardware-tested';self.write_core()
        self.assertTrue(any('lifecycle' in e for e in kb.validate(self.root)))

    def test_usage_requires_our_report(self):
        self.core['our_usage']=[dict(project='fixture',module='fixture',role='test',
                               status='HIL-validated',evidence=self.core['verification']['source']['evidence'])]
        self.write_core()
        self.assertTrue(any('our_usage' in e for e in kb.validate(self.root)))

    def test_tested_compatibility_requires_result(self):
        self.core['toolchains'][0]['status']='tested';self.write_core()
        self.assertTrue(any('tested compatibility' in e for e in kb.validate(self.root)))

    def test_missing_project_rejected(self):
        self.core['project']='missing';self.write_core()
        self.assertTrue(any('missing project' in e for e in kb.validate(self.root)))

    def test_duplicate_core_identity_rejected(self):
        other=dict(self.core,id='another-name')
        (self.core_path.parent/'another-name.yaml').write_text(yaml.safe_dump(other))
        self.assertTrue(any('duplicate IP' in e for e in kb.validate(self.root)))

    def test_repository_alias_duplicate_rejected(self):
        path=self.root/'projects/litex.yaml';p=yaml.safe_load(path.read_text())
        p['aliases']=['https://GITHUB.COM/enjoy-digital/liteeth.git/']
        path.write_text(yaml.safe_dump(p))
        self.assertTrue(any('repository/alias duplicates' in e for e in kb.validate(self.root)))

    def search(self, **kwargs):
        args=Namespace(query=[],hdl=None,license=None,fpga=None,toolchain=None,
                       verification=None,compatibility=None,json=True)
        for key,value in kwargs.items():setattr(args,key,value)
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):kb.search(args,self.root)
        return json.loads(stream.getvalue())

    def test_filter_intersection_and_confidence(self):
        self.assertEqual(len(self.search(query=['ethernet'],fpga='ecp5',toolchain='yosys',
                                        hdl='migen',license='BSD-2-Clause')),1)
        self.assertEqual(self.search(fpga='ecp5',toolchain='yosys',compatibility='tested'),[])
        self.assertEqual(self.search(verification='synthesis=passed'),[])
        self.assertEqual(len(self.search(verification='upstream_testbench=present')),1)

    def test_unsupported_toolchain_does_not_match(self):
        self.core['toolchains'][0]['status']='unsupported';self.write_core()
        self.assertEqual(self.search(toolchain='yosys'),[])

    def test_index_deterministic_and_stale_detected(self):
        (self.root/'docs').mkdir()
        self.assertTrue(kb.render(self.root));self.assertTrue(kb.render(self.root,check=True))
        (self.root/'docs/index.md').write_text('stale')
        self.assertFalse(kb.render(self.root,check=True))

    def test_link_status_classification(self):
        url='https://example.org/repo'
        self.assertEqual(check_urls.classify(url,url,403),'inaccessible')
        self.assertEqual(check_urls.classify(url,url,429),'inaccessible')
        self.assertEqual(check_urls.classify(url,url,404),'broken')
        self.assertEqual(check_urls.classify(url,'https://example.org/users/sign_in',200),'inaccessible')
        self.assertEqual(check_urls.classify(url,'https://example.org/new-repo',200),'moved')
        self.assertEqual(check_urls.classify(url,url,503),'transient_error')
        self.assertEqual(check_urls.classify(url,url+'/',200),'reachable')

    def test_search_aliases(self):
        self.assertTrue(kb.matches('lockin',['digital lock-in']))
        self.assertTrue(kb.matches('100base fx',['100BASE-FX']))
        self.assertTrue(kb.matches('axi stream',['AXI-Stream']))
        self.assertTrue(kb.matches('Zabołotny',['Wojciech Zabolotny']))

    def test_author_search(self):
        path=self.root/'projects/liteeth.yaml'
        project=yaml.safe_load(path.read_text())
        project['organization']='Wojciech M. Zabołotny'
        path.write_text(yaml.safe_dump(project))
        self.assertEqual(len(self.search(query=['Zabolotny'])),1)

    def test_svn_revision_is_explicit_and_pinned(self):
        path=self.root/'projects/liteeth.yaml'
        project=yaml.safe_load(path.read_text())
        project.update(vcs='svn',revision='svn:76')
        project['maintenance']['observed_head_date']=None
        path.write_text(yaml.safe_dump(project))
        self.assertEqual(kb.validate(self.root),[])
        project['revision']='HEAD'
        path.write_text(yaml.safe_dump(project))
        self.assertTrue(kb.validate(self.root))
        project.pop('vcs');project['revision']='svn:76'
        path.write_text(yaml.safe_dump(project))
        self.assertTrue(kb.validate(self.root))


if __name__=='__main__':unittest.main()
