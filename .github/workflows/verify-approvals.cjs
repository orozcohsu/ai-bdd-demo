// G1 provenance: content checks and human approval are separate results.
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const git = (...args) => execFileSync('git', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
const readme = 'features/README.md';
const scope = '整份文件（含核准紀錄狀態差異，請以本次審查確認）';
const specPaths = [
  'specs/functional/functional-spec.md',
  'specs/business/business-rules.md',
  'specs/technical/technical-spec.md',
];

function parseTrace(text) {
  const rows = new Map();
  const start = text.indexOf('### 7.5 ');
  if (start < 0) return rows;
  const rest = text.slice(start).split('\n').slice(1).join('\n');
  const body = rest.split(/^### 7\.6|^## /m)[0];
  for (const line of body.split('\n')) {
    if (!line.trim().startsWith('|')) continue;
    const cells = line.trim().slice(1, -1).split('|').map(c => c.trim());
    if (!cells[0].startsWith('specs/')) continue;
    if (cells.length !== 7 || !specPaths.includes(cells[0]) || rows.has(cells[0])) {
      throw new Error('Invalid or duplicate specification trace row');
    }
    const [path, version, commit, blob, link, coverage, status] = cells;
    if (!/^\d+\.\d+(?:\.\d+)?$/.test(version) || !/^[a-f0-9]{40}$/.test(commit)
        || !/^[a-f0-9]{40}$/.test(blob) || coverage !== scope || status !== 'Pending Review') {
      throw new Error(`Invalid trace fields: ${path}`);
    }
    rows.set(path, { path, version, commit, blob, link, coverage, status });
  }
  return rows;
}

function validateTrace(rows, repo, runGit = git) {
  if (rows.size !== specPaths.length) throw new Error('All three specification trace rows are required');
  for (const row of rows.values()) {
    const expected = `[固定版本](https://github.com/${repo.owner}/${repo.repo}/blob/${row.commit}/${row.path})`;
    if (row.link !== expected) throw new Error(`Invalid fixed content link: ${row.path}`);
    runGit('merge-base', '--is-ancestor', row.commit, 'HEAD');
    if (runGit('rev-parse', `${row.commit}:${row.path}`) !== row.blob
        || runGit('rev-parse', `HEAD:${row.path}`) !== row.blob) {
      throw new Error(`Stale or mismatched specification content: ${row.path}`);
    }
    const content = runGit('show', `${row.commit}:${row.path}`);
    const version = content.match(/\*\*文件版本：\*\*\s*([\d.]+)/)?.[1];
    if (version !== row.version) throw new Error(`Document version mismatch: ${row.path}`);
  }
}

async function verify({ github, context, core, runGit = git, output = 'reports/G1-approval.json' }) {
  const testedSha = runGit('rev-parse', 'HEAD');
  const records = [], missing = [], diagnostics = [];
  let current = new Map();
  let traceValid = false;
  try {
    current = parseTrace(runGit('show', `HEAD:${readme}`));
    validateTrace(current, context.repo, runGit);
    traceValid = true;
    diagnostics.push('Trace structure, versions, fixed links and current content hashes: PASS');
  } catch (error) {
    diagnostics.push(`Trace validation: FAIL (${error.message})`);
  }
  const paths = runGit('ls-tree', '-r', '--name-only', 'HEAD').split('\n')
    .filter(p => /^features\/[^/]+\.feature$/.test(p) || /^specs\/.*\.md$/.test(p));
  if (!paths.length) throw new Error('No requirements or Features to verify');
  const closed = await github.paginate(github.rest.pulls.list, {
    ...context.repo, state: 'closed', per_page: 100,
  });
  const candidates = [];
  for (const pr of closed.filter(p => p.merged_at)) {
    const { data: detail } = await github.rest.pulls.get({ ...context.repo, pull_number: pr.number });
    if (detail.merged_by?.type !== 'User' || !detail.merged_at || !detail.merge_commit_sha
        || detail.base.repo.full_name !== `${context.repo.owner}/${context.repo.repo}`
        || detail.base.ref !== 'main') continue;
    try { runGit('merge-base', '--is-ancestor', detail.merge_commit_sha, 'HEAD'); }
    catch { continue; }
    const files = await github.paginate(github.rest.pulls.listFiles, {
      ...context.repo, pull_number: pr.number, per_page: 100,
    });
    candidates.push({ pr: detail, files: new Set(files.filter(f => f.status !== 'removed').map(f => f.filename)) });
  }
  for (const path of paths) {
    const blob = runGit('rev-parse', `HEAD:${path}`);
    let evidence;
    for (const candidate of candidates) {
      const pr = candidate.pr;
      if (candidate.files.has(path)) {
        try {
          if (runGit('rev-parse', `${pr.merge_commit_sha}:${path}`) === blob) {
            evidence = { method: 'direct-content-PR', pr };
            break;
          }
        } catch { /* A missing file is not approval evidence. */ }
      }
      if (!traceValid || !specPaths.includes(path) || !candidate.files.has(readme)) continue;
      try {
        const approved = parseTrace(runGit('show', `${pr.merge_commit_sha}:${readme}`));
        validateTrace(approved, context.repo, runGit);
        const row = approved.get(path);
        if (JSON.stringify(row) !== JSON.stringify(current.get(path))) continue;
        let previous = new Map();
        try { previous = parseTrace(runGit('show', `${pr.merge_commit_sha}^1:${readme}`)); }
        catch { /* An absent previous table is allowed for its first introduction. */ }
        // An unrelated README edit retaining an existing row is not a new approval.
        if (JSON.stringify(previous.get(path)) === JSON.stringify(row)) continue;
        runGit('merge-base', '--is-ancestor', row.commit, pr.merge_commit_sha);
        evidence = { method: 'historical-content-record-PR', pr };
        break;
      } catch (error) { diagnostics.push(`PR #${pr.number} trace not applicable to ${path}: ${error.message}`); }
    }
    if (evidence) {
      records.push({ path, blob, method: evidence.method, pr: evidence.pr.html_url,
        merged_by: evidence.pr.merged_by.login, merged_at: evidence.pr.merged_at,
        merge_commit: evidence.pr.merge_commit_sha });
    } else missing.push(`${path}: approval NOT VERIFIED / Pending Review; no matching human-merged content or trace-record PR`);
  }
  fs.mkdirSync(require('node:path').dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify({ tested_sha: testedSha, trace_valid: traceValid, diagnostics, records, missing }, null, 2));
  const lines = [...diagnostics, ...records.map(r => `${r.path}: ${r.method}, ${r.pr}, human ${r.merged_by}, merged ${r.merged_at}, content ${r.blob}`), ...missing];
  lines.forEach(line => core.info(line));
  await core.summary.addHeading('G1 trace integrity and human approval (separate results)')
    .addRaw(`Tested commit: ${testedSha}\n`).addList(lines).write();
  if (!traceValid || missing.length) core.setFailed('G1 not complete: trace integrity or human approval remains unverified. Review the fixed specification snapshot in this PR; no Environment wait or automatic approval.');
  return { traceValid, records, missing };
}

module.exports = verify;
module.exports.parseTrace = parseTrace;
module.exports.validateTrace = validateTrace;
