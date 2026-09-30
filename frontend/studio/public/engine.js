// One dispatcher across the local API, desktop sidecar and browser Python.
const nativeFetch = globalThis.__PRABHA_FETCH || globalThis.fetch.bind(globalThis);
const TIMEOUT = 120_000;
let worker, ready, mode = '', status = 'Ready to run', nextId = 0;
const listeners = new Set();
const pending = new Map();

function report(value) {
  status = value;
  for (const callback of listeners) callback(value);
}
export function engineStatus(callback) {
  listeners.add(callback);
  callback(status);
  return () => listeners.delete(callback);
}
export const engineMode = () => mode;

function stopWorker(error) {
  worker?.terminate();
  worker = undefined;
  ready = undefined;
  mode = '';
  for (const {reject, timer} of pending.values()) {
    clearTimeout(timer);
    reject(error);
  }
  pending.clear();
  report('Engine stopped — run again to retry');
}

async function initialize() {
  if (globalThis.__TAURI__?.core?.invoke) {
    mode = 'Desktop Python';
    report(mode);
    return;
  }
  try {
    const response = await nativeFetch('/api/health', {signal: AbortSignal.timeout(1500)});
    if (response.ok && (await response.json()).engine === 'native-python') {
      mode = 'Python API';
      report(mode);
      return;
    }
  } catch { /* Static hosting has no API. */ }
  report('Downloading browser Python…');
  const current = new Worker(new URL('./python-worker.js', import.meta.url));
  worker = current;
  await new Promise((resolve, reject) => {
    let initialized = false;
    const fail = error => {
      clearTimeout(timer);
      if (worker !== current) return;
      stopWorker(error);
      if (!initialized) reject(error);
    };
    const timer = setTimeout(() => fail(new Error('Python download timed out. Check your connection, then run again.')), TIMEOUT);
    current.onmessage = ({data}) => {
      if (worker !== current) return;
      if (data.status) { report(data.status); return; }
      if (data.initError) { fail(new Error(data.initError)); return; }
      if (data.ready) {
        clearTimeout(timer);
        initialized = true;
        mode = 'Browser Python';
        report(mode);
        resolve();
        return;
      }
      const request = pending.get(data.id);
      if (!request) return;
      clearTimeout(request.timer);
      pending.delete(data.id);
      data.error ? request.reject(new Error(data.error)) : request.resolve(data.result);
    };
    current.onerror = event => fail(new Error(event.message || 'Python worker failed. Run again to restart it.'));
    current.onmessageerror = () => fail(new Error('Python response could not be read. Run again to restart it.'));
  });
}

export async function execute(payload) {
  if (!ready) ready = initialize().catch(error => {
    ready = undefined;
    if (worker) stopWorker(error);
    else report('Engine unavailable — run again to retry');
    throw error;
  });
  await ready;
  let response;
  if (mode === 'Desktop Python') {
    response = await globalThis.__TAURI__.core.invoke('simulate', {payload});
  } else if (mode === 'Python API') {
    try {
      const http = await nativeFetch('/api/execute', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload), signal: AbortSignal.timeout(TIMEOUT)
      });
      response = await http.json();
      if (!http.ok && response?.ok !== false) throw new Error('Python API returned HTTP ' + http.status + '.');
    } catch (error) {
      ready = undefined;
      mode = '';
      report('API unavailable — run again to reconnect');
      throw new Error('Python API: ' + error.message);
    }
  } else {
    response = await new Promise((resolve, reject) => {
      const id = ++nextId;
      const timer = setTimeout(() => stopWorker(new Error('Simulation timed out. Run again to restart Python.')), TIMEOUT);
      pending.set(id, {resolve, reject, timer});
      try { worker.postMessage({id, payload}); }
      catch (error) { stopWorker(error); }
    });
  }
  if (!response || typeof response.ok !== 'boolean') throw new Error('The engine returned an invalid response.');
  if (!response.ok) {
    const error = new Error(response.error || 'Simulation failed.');
    error.violations = response.violations || [];
    throw error;
  }
  return response.result;
}
