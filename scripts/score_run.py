#!/usr/bin/env python3
"""Score measured run artifacts against S1–S12; missing evidence never passes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('score_design_io',ROOT/'skills/agent-design-studio/scripts/design_io.py')
D=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(D)
BLOCKS=('The system in one sentence','Key design calls','Who acts and who decides','Top risks by RPN','Launch blockers and owners','Illustrative cost per case','Review status:')
BANNED=('canonical','discriminated','payload binding','digest','idempotency','reciprocal','terminal disposition')


def load(path):
    value=D.load_json(path)
    if not isinstance(value,dict):raise ValueError(str(path)+' must contain a JSON object.')
    return value


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bound_evidence(value, folder, required=()):
    hashes=value.get('sourceHashes',{}) if isinstance(value,dict) else {}
    if not isinstance(hashes,dict) or not hashes or not set(required)<=set(hashes): return False
    try: return all(isinstance(h,str) and digest(Path(folder)/p)==h for p,h in hashes.items())
    except (OSError,TypeError): return False


def binds_file(value,folder,target):
    return any((Path(folder)/p).resolve()==Path(target).resolve() for p in value.get('sourceHashes',{})) and bound_evidence(value,folder)


def independently_graded(g,folder):
    return isinstance(g,dict) and g.get('method')=='independent-agent' and isinstance(g.get('agentId'),str) and bool(g['agentId'].strip()) and bound_evidence(g,folder,('design.json','DESIGN.pdf'))


def score(folder,baseline=None,brief=None,validator_script=None):
    validator=D
    if validator_script:
        spec=importlib.util.spec_from_file_location("score_selected_validator",validator_script)
        validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    folder=Path(folder); results={}
    def put(key,passed,evidence,evaluated=True): results[key]={'pass':bool(passed),'evaluated':evaluated,'evidence':evidence}
    def unavailable(key,reason):put(key,False,reason,False)
    try: report=load(folder/'run-report.json')
    except (OSError,ValueError):report={}
    try: design=load(folder/'design.json'); validation=validator.validate_design(design)
    except (OSError,ValueError,KeyError,TypeError) as e:design=None; validation={'valid':False,'errors':[str(e)]}
    mode=report.get('mode',design.get('runOptions',{}).get('mode','standard') if design else 'standard')
    pages=[]; pdf=None
    try:
        from pypdf import PdfReader
        pdf=PdfReader(folder/'DESIGN.pdf'); pages=[p.extract_text() or '' for p in pdf.pages]
    except Exception as e:pdf_error=str(e)  # malformed PDFs are failed measurements, not scorer crashes
    if pages:
        put('S1', mode in {'lite','standard','full'} and (mode=='full' or len(pages)<=({'lite':4,'standard':12}.get(mode,0))),{'mode':mode,'pages':len(pages),'limit':{'lite':4,'standard':12,'full':None}.get(mode)})
        first=pages[0]; positions=[first.find(b) for b in BLOCKS]
        # A score table has dimension IDs and /4 scores, unlike a plain review line.
        scoretable=bool(re.search(r'\bD(?:[1-9]|1[0-2])\b',first) and re.search(r'\b[0-4]\s*/\s*4\b',first))
        put('S2',all(p>=0 for p in positions) and positions==sorted(positions) and not scoretable,{'blocks':dict(zip(BLOCKS,[p>=0 for p in positions])),'inOrder':positions==sorted(positions),'dimensionTableOnPage1':scoretable})
        text=' '.join(pages[:2]); banned=[w for w in BANNED if re.search(r'(?<!\w)'+r'\s+'.join(re.escape(part) for part in w.split())+r'(?!\w)',text,re.I)]
        try:
            import textstat
            ease=textstat.flesch_reading_ease(text)
            words=textstat.lexicon_count(text,removepunct=True); sentences=textstat.sentence_count(text)
            average=words/sentences if sentences else float('inf')
            put('S4',ease>=50 and average<=20 and not banned,{'fleschReadingEase':ease,'averageWordsPerSentence':average,'bannedTerms':banned,'method':'textstat'})
        except ImportError:unavailable('S4',{'reason':'textstat unavailable; readability not evaluated','bannedTerms':banned})
    else:
        for k in ('S1','S2','S4'):unavailable(k,'PDF inspection unavailable: '+pdf_error)
    try:g=load(folder/'grader.json')
    except (OSError,ValueError):g={}
    independent=independently_graded(g,folder)
    s3=g.get('S3',{})
    if independent and isinstance(s3,dict) and s3.get('evidence'):
        vector=False
        if pdf:
            try:
                ops=[op for p in pdf.pages for operands,op in p.get_contents().operations]
                vector=b'm' in ops and b'l' in ops
            except (AttributeError,TypeError):pass
        put('S3',vector and all(s3.get(k) is True for k in ('taskTreeVector','workflowVector','legibleAt100Percent')),{'independentAgent':g['agentId'],'vectorOperatorsPresent':vector,'judgment':s3})
    else:unavailable('S3','Independent image/100%-zoom grading with matching design/PDF hashes unavailable.')
    build=sorted(p for p in (folder/'build').rglob('*') if p.is_file()) if (folder/'build').exists() else []
    sizes={str(p.relative_to(folder)):p.stat().st_size for p in build}
    put('S5',bool(build) and all(n<=25000 for n in sizes.values()) and (mode!='standard' or sum(sizes.values())<=100000),{'fileBytes':sizes,'totalBytes':sum(sizes.values()),'perFileLimit':25000,'standardTotalLimit':100000})
    seeds=ROOT/'evals/seeded-defects'; seed_results=[]; s7=[]
    try:
        manifest=load(seeds/'manifest.json')
        for case in manifest['cases']:
            checked=validator.validate_design(load(seeds/case['file']))
            ids={e.get('ruleId') for e in checked['errors'] if e.get('ruleId')}
            correct=not checked['valid'] and case['ruleId'] in ids
            entry={'file':case['file'],'expectedRule':case['ruleId'],'observedRules':sorted(ids),'pass':correct}
            if case['suite']=='seven-rules':seed_results.append(entry)
            if case['suite']=='S7':
                rp=folder/'seed-reviews'/(Path(case['file']).stem+'.json')
                try:
                    review=load(rp)
                    severe=review.get('method') in ('self-review','independent-agent') and binds_file(review,folder,seeds/case['file']) and any(i.get('ruleId')==case['ruleId'] and i.get('severity') in ('major','critical') and i.get('evidence') for i in review.get('issues',[]) if isinstance(i,dict))
                except (OSError,ValueError,TypeError):severe=False
                entry=dict(entry,reviewMajorOrCritical=bool(severe)); s7.append(entry)
        put('S6',len(seed_results)==7 and all(x['pass'] for x in seed_results),seed_results)
        put('S7',len(s7)==6 and all(x['pass'] and x['reviewMajorOrCritical'] for x in s7),s7,evaluated=len(s7)==6 and all(x['reviewMajorOrCritical'] for x in s7))
    except (OSError,ValueError,KeyError,TypeError) as e:
        unavailable('S6','Seed artifacts unavailable: '+str(e));unavailable('S7','Seed artifacts/reviewer evidence unavailable: '+str(e))
    s8=g.get('S8',{}); which=brief or s8.get('brief'); n,minimum={'telecom':(8,7),'health-claims':(6,5)}.get(which,(0,0))
    checks=s8.get('checks',[]) if isinstance(s8,dict) else []
    if independent and n and isinstance(checks,list) and len(checks)==n and {x.get('id') for x in checks if isinstance(x,dict)}==set(range(1,n+1)) and all(isinstance(x.get('pass'),bool) and x.get('evidence') for x in checks):
        count=sum(x['pass'] for x in checks);put('S8',count>=minimum,{'brief':which,'found':count,'required':minimum,'checks':checks,'independentAgent':g['agentId']})
    else:unavailable('S8','Complete independent checklist grading with matching source hashes unavailable for '+str(which))
    try:
        final=load(folder/'review.json'); review_valid=validator.validate_review(final,structural_valid=validation['valid'])['valid']
        rounds=sorted(folder.glob('review-round-*.json')); prior=[load(p) for p in rounds]
        preserved={r['round'] for r in prior}==set(range(1,final['round'])) and len(prior)==max(0,final['round']-1)
        valid_prior=all(validator.validate_review(r,structural_valid=True)['valid'] for r in prior)
        declared=report.get('reviewRounds')==[p.name for p in rounds]+['review.json']
        independence=final.get('method')!='independent-agent' or (independent and bound_evidence(g,folder,('review.json',)))
        put('S9',review_valid and preserved and valid_prior and declared and independence,{'reviewValid':review_valid,'preservedRounds':preserved,'priorReviewRecordsValid':valid_prior,'reportedRoundsMatch':declared,'methodEvidence':independence,'method':final.get('method'),'status':final.get('status')})
    except (OSError,ValueError,KeyError,TypeError) as e:unavailable('S9','Review round evidence unavailable: '+str(e))
    try:
        t=load(folder/'test-evidence.json')
        outputs=t.get('briefOutputs',[]); output_checks=[]
        for p in outputs:output_checks.append({'folder':p,'valid':validator.validate_design(load(folder/p/'design.json'))['valid']})
        log=(folder/t['log']).read_text()
        log_bound=bound_evidence(t,folder,(t['log'],)) and bool(re.search(r'(?:Ran\s+\d+\s+tests.*?OK|\d+ passed)',log,re.S))
        complete=log_bound and t.get('exitCode')==0 and type(t.get('passed')) is int and t['passed']>=58 and t.get('failed')==0 and t.get('command') and bound_evidence(t,folder) and len({str((folder/x['folder']).resolve()) for x in output_checks})>=6 and all(x['valid'] for x in output_checks) and validation['valid']
        put('S10',complete,{'testEvidence':t,'briefValidation':output_checks,'currentValidation':validation['valid']},evaluated=bool(t.get('command')))
    except (OSError,ValueError,KeyError,TypeError) as e:unavailable('S10','Actual regression-test evidence or six brief outputs unavailable: '+str(e))
    try:
        b=load(Path(baseline)/'run-report.json') if baseline else {}
        used=report.get('approximateTokensUsed'); before=b.get('approximateTokensUsed')
        comparable=mode=='standard' and b.get('mode')=='standard' and type(used) in (int,float) and type(before) in (int,float) and used>=0 and before>0 and bool(report.get('tokenMethod')) and report['tokenMethod']==b.get('tokenMethod')
        if comparable:put('S11',used<=.6*before,{'tokens':used,'baselineTokens':before,'ratio':used/before,'maximumRatio':.6,'tokenMethod':report['tokenMethod']})
        else:unavailable('S11','Comparable standard-mode host token measurements with the same tokenMethod unavailable; artifact size is not inference usage.')
    except (OSError,ValueError):unavailable('S11','Baseline run report unavailable.')
    try:
        i=load(folder/'interactive-evidence.json'); before=load(folder/i['beforeDesign']); edits=load(folder/i['edits']); checkpoint=load(folder/i['checkpoint'])
        removed=set(i.get('removedTaskIds',[])); components=set(i.get('removedComponentIds',[]))
        before_tasks={x['id'] for x in before['stages']['tasks']['items'] if x['kind']=='task'}
        expected_removed=set(edits.get('removeTaskIds',[]))
        while True:
            children={x['id'] for x in before['stages']['tasks']['items'] if x['kind']=='task' and x['data']['parentId'] in expected_removed}
            if children<=expected_removed:break
            expected_removed|=children
        expected_components={x['id'] for x in before['stages']['components']['items'] if set(x['data']['taskIds'])<=expected_removed}
        checkpoint_matches=checkpoint.get('state')=='awaiting-user' and checkpoint.get('stage')=='tasks' and checkpoint.get('designSha256')==hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()
        def scalar_ids(value):
            if isinstance(value,dict):return set().union(*(scalar_ids(v) for v in value.values())) if value else set()
            if isinstance(value,list):return set().union(*(scalar_ids(v) for v in value)) if value else set()
            return {value} if isinstance(value,str) else set()
        downstream=scalar_ids(design['stages'])|scalar_ids(design.get('semantics',{}))|scalar_ids(design.get('milestones',[]))
        passed=i.get('scripted') is True and design.get('runOptions',{}).get('interactive') is True and bound_evidence(i,folder,('design.json',i['beforeDesign'],i['edits'],i['checkpoint'])) and checkpoint_matches and bool(expected_removed) and removed==expected_removed and removed<=before_tasks and components==expected_components and not (removed|components)&downstream and validation['valid']
        put('S12',passed,{'removedTasks':sorted(removed),'removedComponents':sorted(components),'checkpointMatches':checkpoint_matches,'absentDownstream':not bool((removed|components)&downstream),'validationPass':validation['valid']})
    except (OSError,ValueError,KeyError,TypeError) as e:unavailable('S12','Scripted task-removal/checkpoint evidence unavailable: '+str(e))
    return {'version':'1.1','folder':str(folder),'mode':mode,'brief':brief,'validatorScript':str(validator_script or ROOT/'skills/agent-design-studio/scripts/design_io.py'),'allPass':all(r['pass'] for r in results.values()),'scores':{k:results[k] for k in sorted(results,key=lambda x:int(x[1:]))}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder');p.add_argument('--baseline');p.add_argument('--brief',choices=('telecom','health-claims'));p.add_argument('--out');p.add_argument('--validator-script');a=p.parse_args()
    r=score(a.folder,a.baseline,a.brief,a.validator_script);out=Path(a.out) if a.out else Path(a.folder)/'scorecard.json';out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    for k,v in r['scores'].items():print(k+': '+('PASS' if v['pass'] else 'FAIL')+(' (not evaluated)' if not v['evaluated'] else ''))
    print(json.dumps({'allPass':r['allPass'],'out':str(out)}))
    return 0 if r['allPass'] else 1


if __name__=='__main__':raise SystemExit(main())
