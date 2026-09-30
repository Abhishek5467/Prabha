import test from 'node:test';
import assert from 'node:assert/strict';

let instance = 0;
const nextModule = () => import('../public/engine.js?test=' + (++instance));
const tick = () => new Promise(resolve => setImmediate(resolve));
test('a worker crash rejects every pending request and the next request restarts Python', async t => {
  const previous = {fetch: globalThis.fetch, Worker: globalThis.Worker};
  t.after(() => Object.assign(globalThis, previous));
  const workers = [];
  globalThis.fetch = async () => ({ok: false});
  globalThis.Worker = class {
    constructor() { workers.push(this); queueMicrotask(() => this.onmessage({data: {ready: true}})); }
    postMessage(message) { this.last = message; }
    terminate() { this.terminated = true; }
  };
  const engine = await nextModule();
  const first = engine.execute({action: 'meta'}), second = engine.execute({action: 'infer'});
  const rejected = Promise.all([assert.rejects(first, /worker crashed/), assert.rejects(second, /worker crashed/)]);
  await tick();
  workers[0].onerror({message: 'worker crashed'});
  await rejected;
  assert.equal(workers[0].terminated, true);
  const retry = engine.execute({action: 'meta'});
  await tick();
  assert.equal(workers.length, 2);
  workers[1].onmessage({data: {id: workers[1].last.id, result: {ok: true, result: {version: 'test'}}}});
  assert.deepEqual(await retry, {version: 'test'});
  assert.equal(engine.engineMode(), 'Browser Python');
});
test('API validation errors keep the connection; malformed HTTP responses reconnect', async t => {
  const previous = globalThis.fetch;
  t.after(() => { globalThis.fetch = previous; });
  let failed = false, checks = 0;
  globalThis.fetch = async path => {
    if (path === '/api/health') { checks++; return {ok: true, json: async () => ({engine: 'native-python'})}; }
    return failed ? {ok: false, status: 503, json: async () => { throw new Error('invalid JSON'); }}
      : {ok: false, status: 422, json: async () => ({ok: false, error: 'Invalid inputs'})};
  };
  const engine = await nextModule();
  await assert.rejects(engine.execute({action: 'infer'}), /Invalid inputs/);
  await assert.rejects(engine.execute({action: 'infer'}), /Invalid inputs/);
  assert.equal(checks, 1);
  failed = true;
  await assert.rejects(engine.execute({action: 'infer'}), /Python API/);
  failed = false;
  await assert.rejects(engine.execute({action: 'infer'}), /Invalid inputs/);
  assert.equal(checks, 2);
});
