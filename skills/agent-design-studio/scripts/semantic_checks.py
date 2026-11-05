"""Deterministic checks of declared v1.1 contracts; never executes business tools."""
import json

RULES = {
    'SEM001': 'Every reachable write path passes validation or approval.',
    'SEM002': 'Human waits over one hour branch to a requester notice.',
    'SEM003': 'Each write action class has positive and negative golden cases.',
    'SEM004': 'Golden fixtures are self-contained or use a versioned base and merge rule.',
    'SEM005': 'LLM outputs do not supply money, dates or identity to writes.',
    'SEM006': 'Uncertain writer outcomes reconcile before a repeated write.',
    'SEM007': 'Completion confirmation passes a record-ID guard on every path.',
    'SEM008': 'Every answer golden names a read source component and a citation field.',
    'SEM009': 'A component that reads or writes by record ID is scoped to a tenant.',
}
# A read-only assistant declares its answers the way a writing one declares its
# writes: `answer` is the action class, and its goldens are checked by SEM008
# instead of SEM003.
ANSWER_ACTION = 'answer'
KINDS = {'start','validation','approval','write','human_wait','requester_notice','reconcile','record_id_guard','completion','other'}
CATEGORIES = {'money','date','identity','other'}
OUTCOMES = {'normal','TIMEOUT','unknown_commit','repeat','notice'}


def _has_blanks(value):
    """Is a scaffold blank still in here?

    Only the literal "TODO" marker counts. A null is legitimate in a finished
    contract, so treating every null as a blank would mislabel real errors.
    """
    if isinstance(value, dict):
        return any(_has_blanks(v) for v in value.values())
    if isinstance(value, list):
        return any(_has_blanks(v) for v in value)
    return value == 'TODO'


def validate_semantics(design):
    errors = []
    def issue(rule, message, path='$.semantics'):
        errors.append({'path': path, 'ruleId': rule, 'message': message})
    s = design.get('semantics')
    if not isinstance(s, dict):
        issue('SEM000', 'schemaVersion 1.1 requires complete semantic metadata.')
        return errors
    required = {'version','entrypoints','nodes','transitions','componentEffects','modelOutputs','writeActions','goldens'}
    if set(s) != required or s.get('version') != '1.1':
        issue('SEM000', 'Semantic contract requires exactly: ' + ', '.join(sorted(required)) + '; version must be 1.1.')
    arrays = required - {'version'}
    if any(not isinstance(s.get(k), list) for k in arrays):
        issue('SEM000', 'Every semantic collection must be an explicit array, including empty declarations.')
        return errors
    # Reject malformed metadata before graph/index operations; JSON values such
    # as object IDs and array kinds must produce diagnostics rather than crashes.
    malformed = False
    def shape(rows, required, optional=None):
        nonlocal malformed
        optional = optional or {}
        for row in rows:
            if not isinstance(row, dict) or not set(required) <= set(row) or set(row) - set(required) - set(optional):
                malformed = True; continue
            for key, typ in dict(required, **optional).items():
                if key in row and (not isinstance(row[key], typ) or (typ in (int,float) and isinstance(row[key],bool))):
                    malformed = True
    if any(not isinstance(x,str) for x in s['entrypoints']): malformed = True
    shape(s['nodes'], {'id':str,'kind':str}, {'actionClass':str,'waitHours':(int,float),'bindings':list,'recordProof':(dict,list)})
    shape(s['transitions'], {'from':str,'to':str,'when':str,'outcome':str})
    shape(s['componentEffects'], {'componentId':str,'effect':str})
    shape(s['modelOutputs'], {'componentId':str,'field':str,'category':str})
    shape(s['writeActions'], {'actionClass':str,'nodeIds':list})
    shape(s['goldens'], {'evalId':str,'actionClass':str,'polarity':str}, {'fixture':dict,'base':dict,'mergeRule':str,'overrides':dict,'resolvedFixture':dict,'citationField':str})
    for n in s['nodes']:
        if isinstance(n,dict) and isinstance(n.get('bindings'),list):
            shape(n['bindings'], {'field':str,'category':str,'source':str}, {'sourceComponentId':str,'sourceField':str})
        if isinstance(n,dict) and 'recordProof' in n:
            proofs=n['recordProof'] if isinstance(n['recordProof'],list) else [n['recordProof']]
            shape(proofs, {'field':str,'sourceComponentId':str,'sourceField':str})
    for a in s['writeActions']:
        if isinstance(a,dict) and isinstance(a.get('nodeIds'),list) and any(not isinstance(x,str) for x in a['nodeIds']): malformed=True
    if malformed:
        # An unfinished scaffold is a common cause; say so rather than leaving
        # the author to work out which key is wrong.
        if _has_blanks(s):
            issue('SEM000', 'This semantic contract still holds scaffold blanks ("TODO" or null). '
                            'design_scaffold.py fills the bookkeeping and leaves every business decision '
                            'blank on purpose; fill them before validating.')
        else:
            issue('SEM000', 'Malformed semantic row: use the exact documented keys and JSON value types.')
        return errors
    wf = {x['id']: x for x in design['stages']['workflow']['items']}
    comps = {x['id']: x for x in design['stages']['components']['items']}
    evals = {x['id']: x for x in design['stages']['evals']['items']}
    def indexed(rows, key, label):
        out = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get(key), str) or not row[key] or row[key] in out:
                issue('SEM000', label + ' must contain unique nonempty ' + key + ' declarations.')
            else:
                out[row[key]] = row
        return out
    ns = indexed(s['nodes'], 'id', 'nodes')
    effects = indexed(s['componentEffects'], 'componentId', 'componentEffects')
    actions = indexed(s['writeActions'], 'actionClass', 'writeActions')
    if set(ns) != set(wf): issue('SEM000', 'Semantic nodes must cover every workflow node exactly.')
    if set(effects) != set(comps): issue('SEM000', 'componentEffects must cover every component exactly.')
    for row in effects.values():
        if set(row) != {'componentId','effect'} or row.get('effect') not in {'none','read','write'}:
            issue('SEM000', 'Invalid component effect declaration.')
    for ident, n in ns.items():
        allowed = {'id','kind','actionClass','waitHours','bindings','recordProof'}
        if set(n)-allowed or n.get('kind') not in KINDS:
            issue('SEM000', 'Unknown or missing node semantic kind: ' + ident)
        if ident not in wf: continue
        effect = effects.get(wf[ident]['data']['componentId'], {}).get('effect')
        if (effect == 'write') != (n.get('kind') == 'write'):
            issue('SEM000', 'Write node kind must agree with its component effect: ' + ident)
        if n.get('kind') == 'write' and (not isinstance(n.get('actionClass'), str) or not n['actionClass']):
            issue('SEM000', 'Write needs an actionClass: ' + ident)
        if n.get('kind') == 'human_wait' and (type(n.get('waitHours')) not in (int,float) or n['waitHours'] < 0):
            issue('SEM000', 'Human wait requires nonnegative numeric waitHours: ' + ident)
    # The graph is the actual workflow graph. Semantic edges annotate each contract
    # transition, not a second graph that can quietly remove a dangerous path.
    actual = []
    for ident, w in wf.items():
        try: contract = json.loads(w['description'])
        except (ValueError, TypeError): continue  # structural validator owns malformed JSON
        for tr in contract.get('transitions', []):
            if isinstance(tr, dict): actual.append((ident, tr.get('to'), tr.get('when')))
    triples = []
    edges = []
    for e in s['transitions']:
        if not isinstance(e, dict) or set(e) != {'from','to','when','outcome'} or e.get('from') not in wf or e.get('to') not in wf or e.get('outcome') not in OUTCOMES or not isinstance(e.get('when'), str):
            issue('SEM000', 'Every semantic transition needs valid from/to/when/outcome.')
            continue
        triples.append((e['from'],e['to'],e['when']))
        edges.append(e)
    if sorted(triples) != sorted(actual): issue('SEM000', 'Semantic transitions must exactly annotate actual workflow contract transitions, including predicates.')
    adj = {i: [] for i in wf}
    for i,w in wf.items(): adj[i] = [j for j in w['data']['next'] if j in wf]
    incoming = {j for js in adj.values() for j in js}
    roots = set(wf)-incoming
    entries = s['entrypoints']
    if any(not isinstance(i,str) for i in entries) or len(entries) != len(set(entries)) or set(entries) != roots:
        issue('SEM000', 'Entrypoints must equal all actual workflow roots, without duplicates.')
    def reachable(starts, blocked=()):
        seen = set(); todo = list(starts); blocked = set(blocked)
        while todo:
            i = todo.pop()
            if i in seen or i in blocked: continue
            seen.add(i); todo.extend(adj.get(i, []))
        return seen
    all_reached = reachable(roots)
    def kind(k): return {i for i,n in ns.items() if n.get('kind') in k}
    writes = kind({'write'})
    # Removing all guards and looking for a remaining path checks all paths,
    # including joins, bypasses and cycles; an ancestor somewhere is insufficient.
    unguarded = reachable(roots, kind({'validation','approval'}))
    for i in writes & all_reached & unguarded: issue('SEM001', 'Write is reachable without upstream validation or approval: ' + i)
    for i in kind({'human_wait'}):
        wait = ns[i].get('waitHours')
        if type(wait) in (int,float) and wait > 1:
            notice_edges = [e for e in edges if e['from']==i and e['outcome']=='notice' and ns.get(e['to'],{}).get('kind')=='requester_notice']
            if not notice_edges: issue('SEM002', 'Wait over one hour needs an explicit requester notice branch: ' + i)
    declared_writes = []
    for a,row in actions.items():
        ids = row.get('nodeIds')
        if set(row) != {'actionClass','nodeIds'} or not isinstance(ids,list) or not ids or any(not isinstance(i,str) for i in ids):
            issue('SEM000', 'Each write action needs a nonempty nodeIds array.'); continue
        declared_writes.extend(ids)
        if any(i not in writes or ns[i].get('actionClass') != a for i in ids): issue('SEM000', 'Write action class/node declarations disagree: ' + a)
    if len(declared_writes) != len(set(declared_writes)) or set(declared_writes) != writes:
        issue('SEM000', 'writeActions must cover all write nodes exactly.')
    coverage = set()
    seen_evals = set()
    for g in s['goldens']:
        if not isinstance(g,dict): issue('SEM000','Invalid golden declaration.'); continue
        eid = g.get('evalId'); a = g.get('actionClass'); polarity = g.get('polarity')
        if eid not in evals or evals.get(eid,{}).get('data',{}).get('category') != 'golden' or eid in seen_evals or (a not in actions and a not in ('', ANSWER_ACTION)) or polarity not in {'positive','negative'}:
            issue('SEM000','Golden must identify a unique actual golden eval, declared action class and polarity.'); continue
        seen_evals.add(eid)
        data = evals[eid]['data']
        try: fixture = {'input':json.loads(data['input']), 'expected':json.loads(data['expected'])}
        except (TypeError,ValueError): fixture = None
        # Fixture metadata must mirror the actual eval. External inheritance is
        # allowed only when its exact version and deterministic merge are declared.
        if 'base' in g:
            base=g['base']
            if set(g)-{'citationField'}!={'evalId','actionClass','polarity','base','mergeRule','overrides','resolvedFixture'} or not isinstance(base,dict) or set(base)!={'id','version'} or not all(isinstance(base[k],str) and base[k].strip() for k in base) or g.get('mergeRule')!='deep-merge-v1' or not isinstance(g.get('overrides'),dict) or not isinstance(g.get('resolvedFixture'),dict) or g.get('resolvedFixture')!=fixture:
                issue('SEM004','Inherited golden requires versioned base, deep-merge-v1, overrides and resolvedFixture matching actual eval: '+eid)
        elif set(g)-{'evalId','actionClass','polarity','fixture','citationField'} or not isinstance(g.get('fixture'),dict) or set(g['fixture'])!={'input','expected'} or g['fixture']!=fixture or not all(isinstance(fixture[k],dict) and fixture[k] for k in ('input','expected')):
            issue('SEM004','Self-contained golden fixture must match actual eval input/expected objects: '+eid)
        if a and a != ANSWER_ACTION and fixture and isinstance(fixture['expected'],dict):
            count=fixture['expected'].get('writes')
            try: assertion=json.loads(data['passRule']).get('equals',{}).get('writes')
            except (TypeError,ValueError,AttributeError): assertion=None
            writer_components={wf[i]['data']['componentId'] for i in actions[a]['nodeIds'] if i in wf}
            linked=bool(writer_components.intersection(data['componentIds']))
            if type(count) is not int or (polarity=='positive' and count<1) or (polarity=='negative' and count!=0) or type(assertion) is not int or assertion!=count or not linked:
                issue('SEM003','Write golden needs a linked action writer and integer passRule.equals.writes matching expected.writes and polarity: '+eid)
            else:
                coverage.add((a,polarity))
    if seen_evals != {i for i,e in evals.items() if e['data']['category']=='golden'}:
        issue('SEM000', 'Every actual golden eval requires a fixture declaration; use empty actionClass for read-only cases.')
    for a in actions:
        for p in ('positive','negative'):
            if (a,p) not in coverage: issue('SEM003','Missing '+p+' golden for write action '+a)
    errors.extend(_answer_goldens(design, s, evals, comps))
    errors.extend(_tenant_scope(design, s, comps, wf))
    # Output categories and writer input bindings are exhaustive, so an empty
    # metadata list cannot stand in for a provenance check.
    llms = {i for i,c in comps.items() if c['data']['group']=='Agents (LLM)'}
    def fields(c, side): return {x.split(':',1)[0].rstrip('!') for x in c['data'][side]}
    mo = {}
    for row in s['modelOutputs']:
        if not isinstance(row,dict) or set(row)!={'componentId','field','category'} or row.get('componentId') not in llms or not isinstance(row.get('field'),str) or row.get('category') not in CATEGORIES:
            issue('SEM000','modelOutputs needs componentId/field/category for each actual LLM output.'); continue
        key=(row['componentId'],row['field'])
        if key in mo: issue('SEM000','Duplicate model output category.')
        mo[key]=row['category']
    if set(mo)!={(i,f) for i in llms for f in fields(comps[i],'outputs')}: issue('SEM000','modelOutputs must cover every LLM output exactly.')
    for i in writes:
        comp = comps.get(wf.get(i,{}).get('data',{}).get('componentId'))
        bs = ns[i].get('bindings')
        if not isinstance(bs,list): issue('SEM000','Write requires exhaustive input bindings: '+i); continue
        seen=[]
        for b in bs:
            if not isinstance(b,dict) or set(b)-{'field','category','source','sourceComponentId','sourceField'} or not {'field','category','source'}<=set(b) or not isinstance(b.get('field'),str) or b.get('category') not in CATEGORIES or b.get('source') not in {'llm','trusted','literal'}:
                issue('SEM000','Invalid write input binding: '+i); continue
            seen.append(b['field']); source=b.get('sourceComponentId'); sf=b.get('sourceField')
            from_llm=b['source']=='llm' or source in llms
            if source is not None and (source not in comps or sf not in fields(comps[source],'outputs')): issue('SEM000','Binding source must name an actual component output: '+i)
            if b['source']=='llm' and (source,sf) not in mo: issue('SEM000','LLM binding must name a categorized actual model output: '+i)
            sourcecat=mo.get((source,sf))
            if sourcecat is not None and sourcecat!=b['category']: issue('SEM000','Binding category disagrees with model output category: '+i)
            if from_llm and (b['category'] in {'money','date','identity'} or sourcecat in {'money','date','identity'}): issue('SEM005','LLM output supplies protected write input '+b['field']+' at '+i)
        if comp and (len(seen)!=len(set(seen)) or set(seen)!=fields(comp,'inputs')): issue('SEM000','Bindings must cover every write component input exactly: '+i)
    for e in edges:
        if e['from'] in writes and e['outcome'] in {'TIMEOUT','unknown_commit'}:
            repeated = reachable([e['to']],kind({'reconcile'})) & writes
            if repeated: issue('SEM006','Uncertain writer outcome can repeat a write before reconciliation: '+e['from'])
    def required_string_field(component, side, field):
        return any(':' in value and value.split(':',1)[0].rstrip('!').strip()==field and
                   value.split(':',1)[1].strip().split(' ',1)[0]=='string!' for value in component['data'][side])
    valid_record_guards=set()
    for i in kind({'record_id_guard'}):
        declared=ns[i].get('recordProof',[])
        proofs=declared if isinstance(declared,list) else [declared]
        guard=comps.get(wf.get(i,{}).get('data',{}).get('componentId'))
        try: bindings=json.loads(wf[i]['description']).get('bindings',{})
        except (ValueError,TypeError,KeyError): bindings={}
        expected_bindings={}
        valid=bool(proofs) and guard is not None and guard['data']['group']=='Code: validation'
        for proof in proofs:
            source_id=proof['sourceComponentId'];source=comps.get(source_id)
            producers={n for n in ns if n!=i and wf.get(n,{}).get('data',{}).get('componentId')==source_id and
                       (ns[n].get('kind') in {'write','reconcile'} or effects.get(source_id,{}).get('effect')=='read')}
            valid=valid and source is not None and source['data']['group'] in {'Code: tools','Code: validation'} and \
                  required_string_field(guard,'inputs',proof['field']) and \
                  required_string_field(source,'outputs',proof['sourceField']) and \
                  any(i in reachable([producer]) for producer in producers)
            expected_bindings.setdefault(proof['field'],[]).append({'sourceComponentId':source_id,'sourceField':proof['sourceField']})
        for field, alternatives in expected_bindings.items():
            expected=alternatives if len(alternatives)>1 else alternatives[0]
            valid=valid and isinstance(bindings,dict) and bindings.get(field)==expected
        if valid: valid_record_guards.add(i)
        else: issue('SEM007','Record-ID guard requires a deterministic validator and required string recordProof input from upstream trusted writers, reconcilers or read adapters: '+i)
    for i in kind({'completion'}) & reachable(roots,valid_record_guards):
        issue('SEM007','Completion reachable without a record-ID guard: '+i)
    return errors


def _profile(design):
    intake = design.get('intake')
    if not isinstance(intake, dict): return {}
    profile = intake.get('briefProfile')
    return profile if isinstance(profile, dict) else {}


def _answer_goldens(design, s, evals, comps):
    """SEM008: a read-only design proves its answers the way a writer proves its writes.

    With `briefProfile.writes = false` there is no write action for SEM003 to
    check, so the pair of goldens that matters is a cited answer and a refusal
    when the corpus is silent. Each must name a component that actually reads.
    """
    errors = []
    profile = _profile(design)
    if not profile or profile.get('writes') is not False:
        return errors
    effects = {}
    for row in s.get('componentEffects', []):
        if isinstance(row, dict) and isinstance(row.get('componentId'), str):
            effects[row['componentId']] = row.get('effect')
    answers = [g for g in s.get('goldens', [])
               if isinstance(g, dict) and g.get('actionClass') == ANSWER_ACTION]
    if not answers:
        errors.append({'path': '$.semantics.goldens', 'ruleId': 'SEM008',
                       'message': ('A read-only design needs goldens with actionClass "answer": one that answers '
                                   'with a verifiable citation and one that refuses when the corpus is silent.')})
        return errors
    seen = set()
    for g in answers:
        eid = g.get('evalId')
        path = '$.semantics.goldens[' + str(eid) + ']'
        polarity = g.get('polarity')
        seen.add(polarity)
        row = evals.get(eid)
        if row is None:
            continue
        data = row['data']
        try:
            expected = json.loads(data['expected'])
        except (TypeError, ValueError):
            expected = None
        count = expected.get('citations') if isinstance(expected, dict) else None
        if type(count) is not int:
            errors.append({'path': path, 'ruleId': 'SEM008',
                           'message': 'Answer golden needs an integer expected.citations: ' + str(eid)})
        elif polarity == 'positive' and count < 1:
            errors.append({'path': path, 'ruleId': 'SEM008',
                           'message': 'A positive answer golden must expect at least one citation: ' + str(eid)})
        elif polarity == 'negative' and count != 0:
            errors.append({'path': path, 'ruleId': 'SEM008',
                           'message': 'A negative answer golden refuses, so it expects zero citations: ' + str(eid)})
        readers = [c for c in data['componentIds'] if effects.get(c) == 'read']
        if not readers:
            errors.append({'path': path, 'ruleId': 'SEM008',
                           'message': ('Answer golden must name a source component whose declared effect is read: '
                                       + str(eid))})
        if not isinstance(g.get('citationField'), str) or not g['citationField'].strip():
            errors.append({'path': path, 'ruleId': 'SEM008',
                           'message': 'Answer golden must name the citation field it asserts on: ' + str(eid)})
    for polarity in ('positive', 'negative'):
        if polarity not in seen:
            errors.append({'path': '$.semantics.goldens', 'ruleId': 'SEM008',
                           'message': 'Missing ' + polarity + ' answer golden for the read-only corpus.'})
    return errors


# Words that mean "a record of one customer", which in a shared system must be
# read inside a tenant.
RECORD_ID = ('customerid', 'accountid', 'caseid', 'recordid', 'claimid', 'ticketid', 'orderid',
             'invoiceid', 'userid', 'subscriberid', 'policyid', 'documentid', 'patientid')
TENANT_FIELDS = ('tenant', 'tenantid', 'orgid', 'organisationid', 'organizationid', 'workspaceid', 'clientid')


def _tenant_scope(design, s, comps, wf):
    """SEM009: in a shared system, a record ID without a tenant is a cross-tenant read."""
    errors = []
    profile = _profile(design)
    if not profile or not profile.get('multiTenant'):
        return errors
    effects = {}
    for row in s.get('componentEffects', []):
        if isinstance(row, dict) and isinstance(row.get('componentId'), str):
            effects[row['componentId']] = row.get('effect')

    def names(component, side):
        return [x.split(':', 1)[0].rstrip('!').strip().lower() for x in component['data'][side]]

    for cid, component in comps.items():
        if effects.get(cid) not in ('read', 'write'):
            continue
        inputs = names(component, 'inputs')
        if not any(any(key in field for key in RECORD_ID) for field in inputs):
            continue
        if any(any(key in field for key in TENANT_FIELDS) for field in inputs):
            continue
        errors.append({'path': '$.stages.components.' + cid, 'ruleId': 'SEM009',
                       'message': ('Component ' + cid + ' reads or writes by record ID with no tenant in scope; '
                                   'add a trusted tenant input so one customer cannot reach another.')})
    # Identity bindings carry the tenant, and it is never the model's to supply.
    for node in s.get('nodes', []):
        if not isinstance(node, dict):
            continue
        bindings = node.get('bindings')
        if not isinstance(bindings, list):
            continue
        identity = [b for b in bindings if isinstance(b, dict) and b.get('category') == 'identity']
        if not identity:
            continue
        tenant = [b for b in identity if any(key in str(b.get('field', '')).lower() for key in TENANT_FIELDS)]
        if not tenant:
            errors.append({'path': '$.semantics.nodes.' + str(node.get('id')), 'ruleId': 'SEM009',
                           'message': ('Identity binding at ' + str(node.get('id'))
                                       + ' names no tenant field; a shared system must bind the tenant.')})
            continue
        for binding in tenant:
            if binding.get('source') != 'trusted':
                errors.append({'path': '$.semantics.nodes.' + str(node.get('id')), 'ruleId': 'SEM009',
                               'message': ('The tenant at ' + str(node.get('id')) + ' comes from '
                                           + str(binding.get('source')) + '; it must be trusted, never a model output.')})
    return errors
