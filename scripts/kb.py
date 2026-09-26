#!/usr/bin/env python3
"""Offline catalogue validation, search and deterministic Markdown rendering."""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit, unquote

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

class UniqueLoader(yaml.SafeLoader):
    pass

def mapping(loader, node, deep=False):
    result = {}
    for key, value in node.value:
        key = loader.construct_object(key, deep=deep)
        if key in result:
            raise ValueError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value, deep=deep)
    return result

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)

def load(root=ROOT):
    return [(p, yaml.load(p.read_text(), Loader=UniqueLoader))
            for folder in ('projects', 'catalog') for p in sorted((root / folder).rglob('*.yaml'))]

def repository_key(url):
    parts = urlsplit(url)
    path = unquote(parts.path).rstrip('/')
    if path.endswith('.git'):
        path = path[:-4]
    return parts.netloc.lower() + path.lower()

def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

def validate(root=ROOT):
    schema = json.loads((root / 'schemas/entry.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records = load(root)
    errors, ids, repos, cores = [], set(), {}, set()
    projects = {d.get('id'): d for _, d in records if isinstance(d, dict) and d.get('kind') == 'project'}
    if not records:
        errors.append('Catalogue contains no records')
    for path, data in records:
        prefix = str(path.relative_to(root))
        failures = list(validator.iter_errors(data))
        if failures:
            errors.extend(f'{prefix}: {e.message[:450]}' for e in failures)
            continue
        if data['id'] in ids:
            errors.append(f'{prefix}: duplicate id {data["id"]}')
        ids.add(data['id'])
        if path.stem != data['id']:
            errors.append(f'{prefix}: filename must match id')
        if data['kind'] == 'project':
            for url in [data['repository'], *data['aliases']]:
                key = repository_key(url)
                if key in repos and repos[key] != data['id']:
                    errors.append(f'{prefix}: repository/alias duplicates {repos[key]}: {url}')
                repos[key] = data['id']
        else:
            project = projects.get(data['project'])
            if project is None:
                errors.append(f'{prefix}: missing project {data["project"]}')
            key = (data['project'], data['upstream_path'].rstrip('/'))
            if key in cores:
                errors.append(f'{prefix}: duplicate IP source identity {key}')
            cores.add(key)
            if path.parent.name != data['category']:
                errors.append(f'{prefix}: category does not match directory')
            state_stage = {'simulation-tested':'simulation', 'synthesis-tested':'synthesis',
                           'hardware-tested':'hardware_smoke', 'HIL-validated':'functional_hil',
                           'production-used':'production_deployment'}
            def check_state(state, evidence, context):
                if state in state_stage:
                    allowed = {'simulation-tested':{'our_simulation'},'synthesis-tested':{'our_synthesis'},
                               'hardware-tested':{'our_hardware'},'HIL-validated':{'our_hil'},
                               'production-used':{'our_hardware','our_hil'}}[state]
                    if not any(e['type'] in allowed and e.get('report') for e in evidence):
                        errors.append(f'{prefix}: {context} requires our scoped report for {state}')
            if data['lifecycle'] in state_stage:
                fact = data['verification'][state_stage[data['lifecycle']]]
                if fact['status'] != 'passed':
                    errors.append(f'{prefix}: lifecycle requires passed stage')
                check_state(data['lifecycle'], fact['evidence'], 'lifecycle')
            for usage in data['our_usage']:
                check_state(usage['status'], usage['evidence'], 'our_usage')
        result_types = {
            'simulation': 'our_simulation', 'synthesis': 'our_synthesis',
            'place_and_route': 'our_place_and_route', 'bitstream': 'our_bitstream',
            'hardware_smoke': 'our_hardware', 'functional_hil': 'our_hil',
        }
        for stage, fact in data.get('verification', {}).items():
            if fact['status'] in ('passed', 'failed') and stage in result_types:
                allowed = {result_types[stage], 'our_ci', 'upstream_ci',
                           'upstream_artifact', 'third_party_report'}
                if not any(e['type'] in allowed for e in fact['evidence']):
                    errors.append(f'{prefix}: evidence type does not establish {stage}')
        for field in ('fpga_families', 'toolchains'):
            for item in data.get(field, []):
                if item['status'] == 'tested' and not any(
                    e['type'] in ('our_simulation', 'our_synthesis', 'our_place_and_route',
                                  'our_hardware', 'our_hil', 'our_ci', 'upstream_ci',
                                  'upstream_artifact', 'third_party_report')
                    for e in item['evidence']
                ):
                    errors.append(f'{prefix}: tested compatibility requires result evidence')
        for value in walk(data):
            if value.get('status') in ('passed', 'failed') and 'evidence' in value:
                if not any(e['type'] in ('upstream_ci','upstream_artifact','third_party_report',
                                         'our_simulation','our_synthesis','our_place_and_route',
                                         'our_bitstream','our_hardware','our_hil','our_ci')
                           and (e.get('report') or e['type'] in ('upstream_ci','upstream_artifact','third_party_report'))
                           for e in value['evidence']):
                    errors.append(f'{prefix}: result requires a result artifact, not a claim/source file')
            if value.get('type', '').startswith('our_') and value.get('type') != 'our_review':
                if not value.get('report') or not value.get('revision') or not value.get('toolchain'):
                    errors.append(f'{prefix}: our result needs report, revision and toolchain')
                report = value.get('report', '')
                if report and not urlsplit(report).scheme:
                    target = (root / report).resolve()
                    if not target.is_relative_to(root.resolve()) or not target.is_file():
                        errors.append(f'{prefix}: local result report missing or outside repository')
    return errors

ALIASES = {'ecp5':['lfe5u','lfe5um'], 'lockin':['lock-in','lock in'],
           '100basefx':['100base-fx','100base fx'], 'migen':['python/migen'],
           'axi stream':['axi-stream','axis'], 'yosys':['yosys-nextpnr']}

def normalize(text):
    text = unicodedata.normalize('NFKD', text.lower().replace('ł', 'l'))
    return re.sub(r'[^a-z0-9]+', '', text)

def matches(query, values):
    choices = [query, *ALIASES.get(query.lower(), [])]
    return any(normalize(c) in normalize(v) for c in choices for v in values)

def search(args, root=ROOT):
    records = load(root)
    projects = {d['id']:d for _, d in records if d['kind']=='project'}
    out = []
    for path, core in records:
        if core['kind'] != 'ip':
            continue
        project = projects[core['project']]
        fields = [core['id'],core['name'],core['summary'],*core['tags'],*core['interfaces'],
                  project['name'], project['organization']]
        if not all(matches(q, fields) for q in args.query):
            continue
        if args.hdl and not matches(args.hdl, core['language']):
            continue
        if args.license and not matches(args.license,[core['license']['expression']]):
            continue
        for option, field in ((args.fpga,'fpga_families'), (args.toolchain,'toolchains')):
            if option and not any(matches(option,[c['name']]) and c['status'] != 'unsupported'
                                  and (not args.compatibility or c['status']==args.compatibility)
                                  for c in core[field]):
                break
        else:
            if args.verification:
                stage, _, status = args.verification.partition('=')
                if stage not in core['verification']:
                    raise ValueError(f'Unknown verification stage: {stage}')
                if core['verification'][stage]['status'] != (status or 'passed'):
                    continue
            out.append({**core,'repository':project['repository'],'revision':project['revision'],
                        'maintenance':project['maintenance'], 'file':str(path.relative_to(root))})
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for c in out:
            facts = ', '.join(f'{k}:{v["status"]}' for k,v in c['verification'].items()
                              if v['status'] != 'unknown')
            compat = ', '.join(f'{x["name"]}:{x["status"]}' for x in c['toolchains']) or 'unknown'
            print(f'{c["id"]} | {c["license"]["expression"]} | {c["selection"]["status"]}')
            print(f'  {c["summary"]}\n  {facts}\n  Toolchains: {compat}\n  {c["file"]}')
        print(f'{len(out)} matching IP blocks. Claims/present artifacts are not passing results.')
    return 0

def render(root=ROOT, check=False):
    records = load(root)
    projects = {d['id']:d for _,d in records if d['kind']=='project'}
    cores = [(p,d) for p,d in records if d['kind']=='ip']
    lines = ['# Gateware catalogue', '', '<!-- Generated by scripts/kb.py index; do not edit. -->', '',
             f'{len(projects)} inspected projects; {len(cores)} individually catalogued blocks.', '',
             'Evidence is scoped per block. `present` means an artifact exists; `claimed` means an upstream claim.',
             'Neither means we ran or passed the test. No evidence stage implies another.', '',
             '| Project | Revision | Maintenance |', '|---|---|---|']
    for key,p in sorted(projects.items()):
        lines.append(f'| [{p["name"]}](../projects/{key}.yaml) | `{p["revision"][:12]}` | {p["maintenance"]["status"]} |')
    for category in sorted({d['category'] for _,d in cores}):
        lines += ['',f'## {category}', '', '| IP | Scope / selection | Evidence beyond source |', '|---|---|---|']
        for path,c in cores:
            if c['category'] != category:
                continue
            facts = '; '.join(f'{k}: {v["status"]}' for k,v in c['verification'].items()
                              if k!='source' and v['status']!='unknown') or 'Unknown'
            lines.append(f'| [{c["name"]}](../{path.relative_to(root)}) | {c["reuse_scope"]} / {c["selection"]["status"]} | {facts} |')
    content = '\n'.join(lines)+'\n'
    path = root/'docs/index.md'
    if check:
        return path.exists() and path.read_text() == content
    path.write_text(content)
    return True

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    index = sub.add_parser('index'); index.add_argument('--check', action='store_true')
    find = sub.add_parser('search')
    find.add_argument('query', nargs='*')
    for flag in ('hdl','license','fpga','toolchain','verification'):
        find.add_argument('--'+flag)
    find.add_argument('--compatibility', choices=['claimed','integration_present','tested'])
    find.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        if args.command=='validate':
            errors=validate()
            print('\n'.join(errors) if errors else f'Validated {len(load())} YAML records; references and duplicate identities checked.')
            return bool(errors)
        if args.command=='index':
            ok=render(check=args.check)
            if not ok: print('Generated index is stale.',file=sys.stderr)
            return not ok
        return search(args)
    except (ValueError, yaml.YAMLError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())
