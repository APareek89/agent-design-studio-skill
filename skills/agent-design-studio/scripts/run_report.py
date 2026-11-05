"""Record actual artifact measurements; unavailable host usage stays unavailable."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


# What a host may be missing, and the words the report uses for each. A run
# that could not do one of these is not the same run as one that did, and the
# PASS badge on its own does not say so.
HOST_CAPABILITIES = (
    ('subAgent', 'Review', 'independent agent review', 'self-review (no separate agent available)'),
    ('webSearch', 'Research', 'web research', 'none (no web tool)'),
    ('reportLab', 'PDF', 'rendered', 'skipped'),
    ('node', 'Visual QA', 'run', 'not run'),
    ('questionDialog', 'Intake', 'asked', 'skipped (no question dialog)'),
)


def run_conditions(capabilities):
    """One line a reader can act on: what this run could and could not do.

    A design produced without a separate reviewer, without web search or
    without a rendered PDF is a different artifact from one produced with
    them, and the review status alone does not show it.
    """
    parts = []
    for key, label, available, missing in HOST_CAPABILITIES:
        parts.append(label + ': ' + (available if capabilities.get(key) else missing))
    return '. '.join(parts) + '.'


def detect_capabilities(folder, design=None, review=None):
    """What the host running this design actually had.

    Read from the design's own records where it states them, and from the
    environment where it does not.
    """
    folder = Path(folder)
    design = design or {}
    review = review or {}
    research = design.get('research') if isinstance(design.get('research'), dict) else None
    intake = design.get('intake') if isinstance(design.get('intake'), dict) else None
    try:
        import reportlab  # noqa: F401
        has_reportlab = True
    except ImportError:
        has_reportlab = False
    qa = list(folder.glob('html-qa/**/qa.json')) + list(folder.glob('qa.json'))
    method = str(review.get('method', '')).lower()
    return {
        'subAgent': bool(method) and 'self' not in method,
        'webSearch': bool(research and research.get('performed')),
        'reportLab': has_reportlab and (folder / 'DESIGN.pdf').exists(),
        'node': bool(qa),
        'questionDialog': bool(intake and intake.get('asked')),
    }


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
    capabilities=detect_capabilities(folder,design,review)
    result['hostCapabilities']=capabilities
    result['runConditions']=run_conditions(capabilities)
    (folder/'run-report.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder');p.add_argument('--mode',choices=('lite','standard','full'),default='standard');p.add_argument('--started-at');p.add_argument('--approximate-tokens',type=int);p.add_argument('--token-method');a=p.parse_args()
    if a.approximate_tokens is not None and (a.approximate_tokens<0 or not a.token_method):p.error('Token estimate needs a nonnegative value and explicit measurement method.')
    r=record(a.folder,a.mode,a.started_at,a.approximate_tokens,a.token_method);print(json.dumps({'pageCount':r['pageCount'],'wallTimeSeconds':r['wallTimeSeconds'],'reviewStatus':r['reviewStatus'],'report':str(Path(a.folder)/'run-report.json')}))
if __name__=='__main__':main()
