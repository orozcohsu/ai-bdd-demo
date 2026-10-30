"""G1 automatic checks only; human requirement approval is outside this CI job."""
import ast
import json
import subprocess
import csv
import os
import re
from pathlib import Path
from gherkin.parser import Parser
root = Path('features')
rows = list(csv.DictReader((root / 'feature-index.csv').open(encoding='utf-8-sig')))
if not rows:
    raise SystemExit('No indexed features')
ids, names = set(), set()
for row in rows:
    fid, name = row['Feature_ID'], row['Filename']
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*-[0-9]{3}', fid) or fid in ids or name in names or Path(name).name != name:
        raise SystemExit('Invalid or duplicate Feature ID/file')
    document = Parser().parse((root / name).read_text(encoding='utf-8-sig'))
    if not document['feature']['name'].startswith(fid):
        raise SystemExit('Feature ID mismatch')
    ids.add(fid)
    names.add(name)
if names != {p.name for p in root.glob('*.feature')}:
    raise SystemExit('Index does not match Feature files')
with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
    stream.write(f'## G1 syntax/index\n- Syntax and CSV/file mapping: PASS ({len(rows)} Features)\n')
readme = (root / 'README.md').read_text(encoding='utf-8-sig')
table = {}
for line in readme.splitlines():
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if cells and re.fullmatch(r'[A-Z][A-Z0-9_]*-\d{3}', cells[0]):
        if len(cells) != 5 or cells[0] in table:
            raise SystemExit('Invalid or duplicate README Feature row')
        table[cells[0]] = cells
discrepancies = []
for row in rows:
    cells = table.get(row['Feature_ID'])
    if cells is None:
        discrepancies.append(f"Missing README Feature row: {row['Feature_ID']}")
        continue
    filename = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', cells[3])
    expected = [row['Feature_ID'], row['Domain'], row['Description'], row['Filename'], row['Status'].lower()]
    actual = [*cells[:3], filename, cells[4].lower()]
    if actual != expected:
        discrepancies.append(f"README/CSV mismatch: {row['Feature_ID']}")
if set(table) != ids:
    discrepancies.append('README Feature IDs do not match CSV')
with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
    stream.write('- README/CSV consistency: ' + ('FAIL' if discrepancies else 'PASS') + '\n')
    for problem in discrepancies:
        stream.write(f'- {problem}\n')
if discrepancies:
    raise SystemExit('README consistency failed; Analyst/Human Reviewer must repair source document')

# Verify source-reference existence, not human approval or semantic completeness.
reference_count = 0
scenarios = set()
for feature in root.glob('*.feature'):
    text = feature.read_text(encoding='utf-8-sig')
    document = Parser().parse(text)
    fid = document['feature']['name'].split()[0]
    for child in document['feature']['children']:
        if 'scenario' in child:
            scenarios.add((fid, child['scenario']['name']))
    sources = 0
    for number, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith('#'):
            continue
        match = re.search(r'(specs/[A-Za-z0-9_/-]+\.md)', line)
        if not match:
            continue
        source = Path(match[1])
        if not source.is_file():
            raise SystemExit(f'{feature}:{number}: missing source {source}')
        requirement_ids = re.findall(r'(?:BR-AUTH|FUNC|TECH|SEC|UI|CODE|QA|DEPLOY)-[0-9]{3}(?:-[0-9]{3})?', line)
        if not requirement_ids:
            raise SystemExit(f'{feature}:{number}: no requirement IDs in source reference')
        source_text = source.read_text(encoding='utf-8-sig')
        for requirement in requirement_ids:
            if not re.search(r'(?<![A-Z0-9-])' + re.escape(requirement) + r'(?![A-Z0-9-])', source_text):
                raise SystemExit(f'{feature}:{number}: unknown {requirement} in {source}')
            reference_count += 1
        sources += 1
    if not sources:
        raise SystemExit(f'{feature}: no existing source references')

# Check the existing human-readable coverage list against real scenario decorators.
coverage = {}
for number, line in enumerate(Path('tests/COVERAGE.md').read_text(encoding='utf-8').splitlines(), 1):
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if not cells or cells[0] not in ids:
        continue
    if len(cells) != 3:
        raise SystemExit(f'tests/COVERAGE.md:{number}: invalid coverage row')
    key = (cells[0], cells[1])
    if key in coverage:
        raise SystemExit(f'tests/COVERAGE.md:{number}: duplicate Scenario row')
    link = re.fullmatch(r'\[([^]]+)::([A-Za-z_][A-Za-z0-9_]*)\]\(([^)]+)\)', cells[2])
    if not link:
        raise SystemExit(f'tests/COVERAGE.md:{number}: invalid test link')
    label, function, relative = link.groups()
    path = Path('tests') / relative
    if not path.is_file() or path.name != label:
        raise SystemExit(f'tests/COVERAGE.md:{number}: missing or mismatched test path')
    functions = [n for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n, ast.FunctionDef) and n.name == function]
    if len(functions) != 1:
        raise SystemExit(f'{path}: missing or duplicate {function}')
    binding = []
    for dec in functions[0].decorator_list:
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == 'scenario':
            binding.append(tuple(ast.literal_eval(arg) for arg in dec.args))
    expected_file = next(row['Filename'] for row in rows if row['Feature_ID'] == key[0])
    if binding != [(expected_file, key[1])]:
        raise SystemExit(f'tests/COVERAGE.md:{number}: Scenario does not match test decorator')
    coverage[key] = relative + '::' + function
if set(coverage) != scenarios:
    raise SystemExit(f'Coverage/Scenario mismatch: missing={scenarios-set(coverage)}, extra={set(coverage)-scenarios}')
summary = f'- Existing source requirement references: PASS ({reference_count} explicit IDs)\n- Scenario/coverage/test mapping: PASS ({len(scenarios)} Scenarios/Outlines)\n- Human requirement approval: outside CI; not inferred from automated PASS\n'
with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
    stream.write(summary)
Path('reports').mkdir(exist_ok=True)
Path('reports/G1-automatic.json').write_text(json.dumps({
    'tested_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'features': len(rows), 'scenarios_outlines': len(scenarios),
    'explicit_source_ids_checked': reference_count, 'coverage': [dict(feature=k[0], scenario=k[1], test=v) for k,v in sorted(coverage.items())],
    'human_approval': 'outside CI; no approval decision made',
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(summary)
