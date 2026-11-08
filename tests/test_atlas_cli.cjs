'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const {main, pythonCandidates} = require('../plugins/fo-data-atlas/scripts/atlas-cli.cjs');
const silent = {log() {}, error() {}};

test('explicit interpreter path is one argument and disables discovery', () => {
  assert.deepEqual(pythonCandidates({FO_ATLAS_PYTHON: 'C:\\A B\\python.exe'}, 'win32'),
    [['C:\\A B\\python.exe', []]]);
});
test('default enters reviewed setup, retaining terminal and caller cwd', () => {
  const calls = [];
  const run = (exe, args, opts) => {calls.push({exe, args, opts}); return {status: 0};};
  assert.equal(main([], run, silent), 0);
  const launch = calls.at(-1);
  assert.equal(launch.args.at(-1), 'install');
  assert.equal(launch.opts.stdio, 'inherit');
  assert.equal(launch.opts.shell, undefined);
  assert.equal(launch.opts.cwd, undefined);
});
test('update uses existing installer; paths remain literal; exit status propagates', () => {
  const calls = [];
  const run = (exe, args) => {calls.push(args); return {status: args.includes('-c') ? 0 : 7};};
  assert.equal(main(['update', '--destination', 'C:\\Project & data', '--tag', 'v0.4.0'], run, silent), 7);
  assert.deepEqual(calls.at(-1).slice(-5), ['install', '--destination', 'C:\\Project & data', '--tag', 'v0.4.0']);
});
test('missing or outdated Python stops before installation', () => {
  const calls = [];
  const run = (exe, args) => {calls.push(args); return {status: 1};};
  assert.equal(main([], run, silent), 2);
  assert.ok(calls.every(args => args.includes('-c')));
});
test('help and invalid commands do not start Python or network operations', () => {
  const run = () => {throw Error('unexpected execution');};
  assert.equal(main(['--help'], run, silent), 0);
  assert.equal(main(['unknown'], run, silent), 2);
});
test('check remains read-only and child errors return failure', () => {
  const calls = [];
  const run = (exe, args) => {calls.push(args); return args.includes('-c') ? {status: 0} : {status: null, error: Error('fixture')};};
  assert.equal(main(['check'], run, silent), 2);
  assert.equal(calls.at(-1).at(-1), 'check');
});
