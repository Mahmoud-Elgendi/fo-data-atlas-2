#!/usr/bin/env node
'use strict';
// Thin, buildless entrance to the existing verified Python release installer.
// No npm lifecycle scripts, dependencies, shell interpolation or metadata copies.
const {spawnSync} = require('node:child_process');
const path = require('node:path');
const os = require('node:os');

function pythonCandidates(env = process.env, platform = process.platform) {
  if (env.FO_ATLAS_PYTHON) return [[env.FO_ATLAS_PYTHON, []]];
  const candidates = [];
  if (platform === 'win32') {
    candidates.push([path.join(env.USERPROFILE || os.homedir(), '.cache', 'codex-runtimes',
      'codex-primary-runtime', 'dependencies', 'python', 'python.exe'), []], ['py', ['-3']]);
  }
  return candidates.concat([['python3', []], ['python', []]]);
}

function main(args = process.argv.slice(2), run = spawnSync, out = console) {
  if (args.includes('--help') || args.includes('-h')) {
    out.log('F&O Data Atlas - Developed by Mahmoud Elgendi\n' +
      'Building D365 F&O, Microsoft Fabric and AI-assisted SQL solutions.\n' +
      'Mobile / WhatsApp: 00966542128150 | www.mahmoudelgendi.com\n' +
      'fo-data-atlas [install|update|check] [--tag vX.Y.Z] [--destination PATH]\n' +
      'No command opens setup. update opens the same reviewed upgrade wizard.\n' +
      'Requires Python 3.10+, authenticated GitHub CLI and private repository access.\n' +
      'Set FO_ATLAS_PYTHON to an interpreter path if automatic discovery fails.');
    return 0;
  }
  let command = args[0] && !args[0].startsWith('-') ? args.shift() : 'install';
  if (command === 'update') command = 'install';
  if (!['install', 'check', 'download'].includes(command)) {
    out.error('Unknown command. Run fo-data-atlas --help.'); return 2;
  }
  for (const [executable, prefix] of pythonCandidates()) {
    const probe = run(executable, [...prefix, '-c',
      'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'],
      {encoding: 'utf8', windowsHide: true, timeout: 10000});
    if (probe.error || probe.status !== 0) continue;
    // Inherit the caller's project directory and interactive terminal.
    const result = run(executable, [...prefix, path.join(__dirname, 'github_release.py'), command, ...args],
      {stdio: 'inherit', windowsHide: true});
    if (result.error) out.error('Atlas could not start: ' + result.error.message);
    return result.status === null || result.status === undefined ? 2 : result.status;
  }
  out.error('Python 3.10+ was not found. Install Python, reopen the terminal, and retry.\n' +
    'Alternatively set FO_ATLAS_PYTHON to your Python executable.');
  return 2;
}

module.exports = {main, pythonCandidates};
if (require.main === module) process.exitCode = main();
