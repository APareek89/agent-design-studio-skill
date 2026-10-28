"""Score thresholds and missing-evidence behavior; no invented grader decisions."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from test_design_io import make_review
from test_semantics import make_semantic_design

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('score_run',ROOT/'scripts/score_run.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)


class FakePage:
    def __init__(self,text):self.text=text
    def extract_text(self):return self.text
    def get_contents(self):return types.SimpleNamespace(operations=[([],b'm'),([],b'l')])


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name)
        self.write('design.json',make_semantic_design());self.write('review.json',make_review())
        self.write('run-report.json',{'mode':'standard','reviewRounds':['review.json'],'approximateTokensUsed':None,'tokenMethod':'unavailable'})
        (self.folder/'DESIGN.pdf').write_bytes(b'%PDF mock read by fake dependency')
        (self.folder/'build').mkdir();(self.folder/'build/00-overview.md').write_text('Build the design.')
        self.text='\n'.join(S.BLOCKS)+'\nThis tool helps a team handle a request. It keeps clear rules.'
    def write(self,name,obj):
        p=self.folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj));return p
    def hashes(self,*names):return {n:S.digest(self.folder/n) for n in names}
    def run_score(self,text=None,count=3,baseline=None):
        pdf=types.SimpleNamespace(PdfReader=lambda p:types.SimpleNamespace(pages=[FakePage(self.text if text is None else text)]+[FakePage('A simple page.')]*(count-1)))
        ts=types.SimpleNamespace(flesch_reading_ease=lambda text:60,lexicon_count=lambda text,removepunct:100,sentence_count=lambda text:10)
        with patch.dict(sys.modules,{'pypdf':pdf,'textstat':ts}):return S.score(self.folder,baseline,'telecom')['scores']
    def grader(self):
        g={'method':'independent-agent','agentId':'grader-other-context','sourceHashes':self.hashes('design.json','DESIGN.pdf','review.json'),'S3':{'taskTreeVector':True,'workflowVector':True,'legibleAt100Percent':True,'evidence':['Rendered task/workflow pages viewed at 100%.']},'S8':{'brief':'telecom','checks':[{'id':n,'pass':True,'evidence':['Specific design contract inspected.']} for n in range(1,9)]}}
        self.write('grader.json',g);return g
    def test_missing_evidence_never_passes(self):
        r=self.run_score()
        for n in ('S3','S7','S8','S10','S11','S12'):
            self.assertFalse(r[n]['pass'],n);self.assertFalse(r[n]['evaluated'],n)
        for n in ('S1','S2','S4','S5','S6','S9'):self.assertTrue(r[n]['pass'],(n,r[n]))
    def test_mode_limits_are_unchanged(self):
        self.assertFalse(self.run_score(count=13)['S1']['pass'])
        report=json.loads((self.folder/'run-report.json').read_text());report['mode']='lite';self.write('run-report.json',report)
        self.assertTrue(self.run_score(count=4)['S1']['pass']);self.assertFalse(self.run_score(count=5)['S1']['pass'])
        report['mode']='full';self.write('run-report.json',report);self.assertTrue(self.run_score(count=50)['S1']['pass'])
    def test_exact_brief_blocks_order_and_score_table(self):
        self.assertFalse(self.run_score(text=self.text.replace('Key design calls','Choices'))['S2']['pass'])
        self.assertFalse(self.run_score(text=self.text+' D1 3/4')['S2']['pass'])
        self.assertFalse(self.run_score(text='\n'.join(reversed(S.BLOCKS)))['S2']['pass'])
    def test_banned_whole_words_and_phrase_line_wrap(self):
        self.assertFalse(self.run_score(text=self.text+' Digest')['S4']['pass'])
        self.assertFalse(self.run_score(text=self.text+' payload\nbinding')['S4']['pass'])
        self.assertTrue(self.run_score(text=self.text+' digested')['S4']['pass'])
    def test_handoff_per_file_size(self):
        (self.folder/'build/large.md').write_bytes(b'x'*(25*1024+1));self.assertFalse(self.run_score()['S5']['pass'])
    def test_independent_grader_hash_binding_and_threshold(self):
        g=self.grader();r=self.run_score();self.assertTrue(r['S3']['pass']);self.assertTrue(r['S8']['pass'])
        for x in g['S8']['checks'][:2]:x['pass']=False
        self.write('grader.json',g);self.assertFalse(self.run_score()['S8']['pass'])
        (self.folder/'DESIGN.pdf').write_bytes(b'changed');self.assertFalse(self.run_score()['S3']['pass'])
    def test_tokens_must_be_host_measurements_same_method(self):
        base=self.folder/'baseline';base.mkdir()
        self.write('baseline/run-report.json',{'mode':'standard','approximateTokensUsed':1000,'tokenMethod':'host-counter-v1'})
        self.write('run-report.json',{'mode':'standard','approximateTokensUsed':600,'tokenMethod':'host-counter-v1'})
        self.assertTrue(self.run_score(baseline=base)['S11']['pass'])
        self.write('run-report.json',{'mode':'standard','approximateTokensUsed':601,'tokenMethod':'host-counter-v1'})
        self.assertFalse(self.run_score(baseline=base)['S11']['pass'])
        self.write('run-report.json',{'mode':'standard','approximateTokensUsed':100,'tokenMethod':'artifact-estimate'})
        self.assertFalse(self.run_score(baseline=base)['S11']['evaluated'])
    def test_review_round_missing_and_false_pass_fail(self):
        review=make_review();review['round']=2;self.write('review.json',review)
        self.assertFalse(self.run_score()['S9']['pass'])
        review=make_review();review['dimensions'][0]['score']=0;self.write('review.json',review)
        self.assertFalse(self.run_score()['S9']['pass'])
    def test_regression_file_cannot_replace_actual_log_or_repeat_one_brief(self):
        self.write('test-evidence.json',{'command':'python -m unittest','exitCode':0,'passed':70,'failed':0,'briefOutputs':['.']*6,'sourceHashes':self.hashes('design.json')})
        self.assertFalse(self.run_score()['S10']['pass'])
        (self.folder/'tests.log').write_text('Ran 70 tests in 1.0s\nOK\n')
        t=json.loads((self.folder/'test-evidence.json').read_text());t.update(log='tests.log',sourceHashes=self.hashes('tests.log','design.json'));self.write('test-evidence.json',t)
        self.assertFalse(self.run_score()['S10']['pass'])
    def test_author_claim_is_not_independent_grading(self):
        g=self.grader();g['method']='self-review';self.write('grader.json',g)
        self.assertFalse(self.run_score()['S3']['evaluated']);self.assertFalse(self.run_score()['S8']['evaluated'])


if __name__=='__main__':unittest.main()
