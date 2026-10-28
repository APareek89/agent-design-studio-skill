"""Observable v2 PDF and context-boundary checks; retain all v1 regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import test_design_io
import test_design_pdf

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/agent-design-studio/scripts'

def module(name):
    spec=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class ModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.folder=Path(self.tmp.name)
        self.d=test_design_io.make_design();self.r=test_design_io.make_review()
        self.d['presentation']={'systemSentence':'Help staff review a request with proof.',
             'designCalls':[{'choice':'Code checks facts.','rejected':'Model maths','why':'Rules stay clear'},
                            {'choice':'People own choices.','rejected':'Free writes','why':'Staff keep control'},
                            {'choice':'Show sources.','rejected':'Guesses','why':'Proof supports review'}],
             'autonomy':[{'action':'Draft a reply','level':'suggests'},{'action':'Approve a decision','level':'human decides'}]}
        self.dp=self.folder/'design.json';self.rp=self.folder/'review.json';self.write()
    def write(self):
        self.dp.write_text(json.dumps(self.d));self.rp.write_text(json.dumps(self.r))
    def tearDown(self):self.tmp.cleanup()
    def test_reexport_removes_only_unchanged_obsolete_milestones(self):
        milestone={'id':'01','title':'First','taskIds':['T1'],'componentIds':['C1'],'evalIds':['EV1','EV2','EV3','EV4'],'acceptanceCriteria':['Keep safe.']}
        self.d['milestones']=[milestone,dict(milestone,id='02',title='Obsolete',acceptanceCriteria=['REMOVED_ACCEPTANCE'])]
        self.write();out=self.folder/'out'
        test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
        stale=out/'build/02-milestone.md';self.assertTrue(stale.exists())
        self.d['milestones']=self.d['milestones'][:1];self.write()
        test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
        self.assertFalse(stale.exists())
        self.assertNotIn('REMOVED_ACCEPTANCE',''.join(p.read_text() for p in (out/'build').glob('*.md')))

    def test_edited_obsolete_file_blocks_export_without_deletion(self):
        out=self.folder/'out';test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
        owned=out/'build/01-milestone.md';owned.write_text('Human edit')
        with self.assertRaisesRegex(ValueError,'edited'):
            test_design_io.design_io.export_design(self.dp,out,self.rp,mode='lite')
        self.assertEqual(owned.read_text(),'Human edit')

    def test_lite_reexport_and_standard_to_lite_are_safe(self):
        out=self.folder/'out';test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
        test_design_io.design_io.export_design(self.dp,out,self.rp,mode='lite')
        self.assertFalse((out/'build').exists());self.assertFalse((out/'PRD.md').exists())
        self.assertTrue(test_design_io.design_io.export_design(self.dp,out,self.rp,mode='lite')['ok'])

    def test_mode_and_reader_metadata_types_are_checked(self):
        bad=copy.deepcopy(self.d);bad['runOptions']={'mode':'tiny','interactive':'yes'}
        self.assertFalse(test_design_io.design_io.validate_design(bad)['valid'])
        bad=copy.deepcopy(self.d);bad['presentation']['autonomy'][0]['level']='unlimited'
        self.assertFalse(test_design_io.design_io.validate_design(bad)['valid'])
        bad=copy.deepcopy(self.d);bad['presentation']['designCalls']=bad['presentation']['designCalls'][:1]
        self.assertFalse(test_design_io.design_io.validate_design(bad)['valid'])

    def test_selected_workflow_contract_cannot_be_dropped(self):
        self.d['milestones']=[{'id':'01','title':'Selected work','taskIds':['T1'],'componentIds':['C1'],'workflowIds':[],
                              'evalIds':['EV1','EV2','EV3','EV4'],'acceptanceCriteria':['Check all outcomes.']}]
        self.write()
        with self.assertRaisesRegex(ValueError,'Every workflow contract'):
            test_design_io.design_io.export_design(self.dp,self.folder/'out',self.rp,mode='standard')

    def test_scripted_checkpoint_removes_task_and_owned_component(self):
        spec=importlib.util.spec_from_file_location('check_interactive',ROOT/'scripts/check_interactive.py')
        check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
        result=check.run(self.folder/'proof')
        after=json.loads((self.folder/'proof/after.json').read_text())
        self.assertEqual(result['removedTaskIds'],['T99'])
        self.assertEqual(result['removedComponentIds'],['C99'])
        self.assertTrue(test_design_io.design_io.validate_design(after)['valid'])
        self.assertNotIn('C99',json.dumps(after))
        self.assertNotIn('T99',json.dumps(after))

    def test_standard_split_keeps_exact_contracts_and_avoids_whole_design_dump(self):
        result=test_design_io.design_io.export_design(self.dp,self.folder/'out',self.rp,mode='standard')
        self.assertTrue(result['ok'],result)
        out=self.folder/'out';files=list((out/'build').glob('*.md'))
        self.assertGreaterEqual(len(files),2)
        self.assertFalse((out/'build-prompt.md').exists())
        self.assertLessEqual(sum(f.stat().st_size for f in files),100000)
        self.assertTrue(all(f.stat().st_size<=25000 for f in files))
        text='\n'.join(f.read_text() for f in files)
        self.assertIn('requestId:string!',text)
        self.assertIn('EV1',text);self.assertNotIn('"stages":',text)
        self.assertIn('Would you also like a visual HTML',text)
        test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
        files[0].write_text('User edit')
        with self.assertRaisesRegex(ValueError,'unrelated or edited'):
            test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
    def test_oversized_standard_handoff_fails_without_hiding_contract(self):
        # Real long contract bypasses stage-schema bound on one string via many allowed values.
        self.d['stages']['components']['items'][0]['data']['inputs']=['field'+str(i)+':string! '+'z'*1000 for i in range(40)]
        self.write()
        with self.assertRaisesRegex(ValueError,'Build context exceeds'):
            test_design_io.design_io.export_design(self.dp,self.folder/'out',self.rp,mode='standard')
        self.assertFalse((self.folder/'out').exists())
    def test_build_output_symlink_is_never_followed(self):
        out=self.folder/'out';out.mkdir();elsewhere=self.folder/'elsewhere';elsewhere.mkdir()
        (out/'build').symlink_to(elsewhere,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlink'):
            test_design_io.design_io.export_design(self.dp,out,self.rp,mode='standard')
        self.assertFalse(list(elsewhere.iterdir()))
    @unittest.skipUnless(test_design_pdf.PDF_AVAILABLE,'PDF runtime optional')
    def test_pdf_modes_pages_real_paths_and_page_one(self):
        from pypdf import PdfReader
        for mode,limit in [('lite',4),('standard',12),('full',None)]:
            target=self.folder/(mode+'.pdf')
            result=test_design_pdf.design_pdf.create_pdf(self.dp,self.rp,target,mode=mode)
            self.assertTrue(result['ok'],result)
            reader=PdfReader(target)
            if limit:self.assertLessEqual(len(reader.pages),limit)
            first=reader.pages[0].extract_text()
            for block in ['The system in one sentence','Key design calls','Who acts and who decides','Top risks by RPN','Launch blockers and owners','Illustrative cost per case','Review status:']:
                self.assertIn(block,first)
            self.assertNotIn('D12',first)
            # PDF path operators demonstrate actual vector drawings rather than a text source diagram.
            content=reader.pages[1].get_contents().get_data()
            self.assertIn(b' c',content);self.assertIn(b' l',content)
            self.assertNotIn('flowchart TD',reader.pages[1].extract_text())
    def test_interactive_removal_invalidates_all_downstream_stages(self):
        session=module('design_session')
        task=copy.deepcopy(self.d['stages']['tasks']['items'][1]);task['id']='T2';task['title']='Optional extra task'
        self.d['stages']['tasks']['items'].append(task)
        cp=self.folder/'checkpoint.json';session.checkpoint(self.d,'tasks',cp)
        edited,removed=session.apply_task_edits(self.d,{'removeTaskIds':['T2']})
        self.assertEqual(removed,['T2'])
        self.assertNotIn('T2',{t['id'] for t in edited['stages']['tasks']['items']})
        self.assertFalse(edited['stages']['components']['items'])
        # Rebuild from accepted task tree with the original C1 (only T1).
        for key in session.ORDER[2:]:edited['stages'][key]=copy.deepcopy(self.d['stages'][key])
        result=test_design_io.design_io.validate_design(edited)
        self.assertTrue(result['valid'],result)
        with self.assertRaises(ValueError):session.apply_task_edits(self.d,{'removeTaskIds':['T0']})

if __name__=='__main__':unittest.main()
