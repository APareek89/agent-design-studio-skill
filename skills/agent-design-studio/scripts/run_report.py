"""Record actual artifact measurements; unavailable host usage stays unavailable."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def record(folder, mode, started_at=None, approximate_tokens=None, token_method=None):
    folder=Path(folder)
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('run_design_io',Path(__file__).with_name('design_io.py'));D=module_from_spec(spec);spec.loader.exec_module(D)
    design=D.load_json(folder/'design.json');validation=D.validate_design(design)
    review=D.load_json(folder/'review.json')
    pages=None
    if (folder/'DESIGN.pdf').exists():
        from pypdf import PdfReader
        pages=len(PdfReader(folder/'DESIGN.pdf').pages)
    now=datetime.now(timezone.utc)
    start=datetime.fromisoformat(started_at.replace('Z','+00:00')) if started_at else None
    if start and start.tzinfo is None:raise ValueError('Start time must include timezone.')
    if start and start>now:raise ValueError('Start time cannot be in the future.')
    files={str(p.relative_to(folder)):p.stat().st_size for p in folder.rglob('*') if p.is_file() and p.name not in ('run-report.json','scorecard.json','grader.json') and '.work' not in p.parts}
    text_files=[p for p in folder.rglob('*') if p.is_file() and p.suffix in ('.json','.md','.csv') and p.name not in ('run-report.json','scorecard.json','grader.json') and not p.name.startswith('review-round-')]
    # A comparable deterministic proxy, reported separately from host tokens.
    text_chars=sum(len(p.read_text()) for p in text_files)
    result={'version':'1.1','mode':mode,'startedAt':started_at,'endedAt':now.isoformat(),
            'wallTimeSeconds':(now-start).total_seconds() if start else None,
            'approximateTokensUsed':approximate_tokens,'tokenMethod':token_method or 'Unavailable: the host did not expose total inference usage.',
            'artifactTextTokenEstimate':round(text_chars/4),'artifactTokenMethod':'UTF-8 decoded text characters / 4 across delivered text artifacts, excludes historical failed rounds; not host inference tokens.',
            'fileSizes':files,'pageCount':pages,'validatorResults':validation,'reviewRounds':sorted(p.name for p in folder.glob('review-round-*.json'))+['review.json'],
            'reviewMethod':review['method'],'reviewStatus':review['status'],
            'designSha256':hashlib.sha256((folder/'design.json').read_bytes()).hexdigest(),
            'businessAssertionsExecuted':False}
    (folder/'run-report.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder');p.add_argument('--mode',choices=('lite','standard','full'),default='standard');p.add_argument('--started-at');p.add_argument('--approximate-tokens',type=int);p.add_argument('--token-method');a=p.parse_args()
    if a.approximate_tokens is not None and (a.approximate_tokens<0 or not a.token_method):p.error('Token estimate needs a nonnegative value and explicit measurement method.')
    r=record(a.folder,a.mode,a.started_at,a.approximate_tokens,a.token_method);print(json.dumps({'pageCount':r['pageCount'],'wallTimeSeconds':r['wallTimeSeconds'],'reviewStatus':r['reviewStatus'],'report':str(Path(a.folder)/'run-report.json')}))
if __name__=='__main__':main()
