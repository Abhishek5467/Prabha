import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {version} from '../package.json';
import {DEFAULT_INPUTS, DEFAULT_NETWORK, PRECISIONS, validateInputs, parseNetwork,
  numberInRange, importAnn, isReference, batchCsv} from './experiments.js';
import {LineChart, Network} from './visuals.jsx';
import './style.css';
import './release.css';

const base = new URL(import.meta.env.BASE_URL, document.baseURI).href;
const engine = import(/* @vite-ignore */ base + 'engine.js');
const platform = import(/* @vite-ignore */ base + 'platform.js');
const fmt = (n, d = 6) => Number.isFinite(n) ? n.toFixed(d) : '—';
const sci = n => Number.isFinite(n) ? n.toExponential(4) : '—';
const nav = [['start', 'Get started', '◇'], ['ann', 'ANN inference', '◉'],
  ['neuron', 'Single neuron', '⊙'], ['components', 'Component lab', '∿'],
  ['evidence', 'Validation archive', '▤']];
const headings = {
  start: ['Light, models and reproducible experiments.', 'Explore photonic-electronic computation, from a device response to a small neural network.'],
  ann: ['Photonic ANN inference', 'Run the 4 → 3 → 2 network and compare physical-model outputs with the analytical reference.'],
  neuron: ['Inside a photonic neuron', 'Follow optical weighting, charge accumulation, activation and readout.'],
  components: ['Explore the device physics', 'Change a model parameter and inspect its response.'],
  evidence: ['A reproducible foundation', 'Browse the original experiments and evidence behind the preview.']
};
const currentView = () => nav.some(([key]) => '#' + key === location.hash) ? location.hash.slice(1) : 'start';
const initialSettings = () => ({inputs: [...DEFAULT_INPUTS], dac_bits: 12, adc_bits: 12,
  network: JSON.stringify(DEFAULT_NETWORK, null, 2)});

function Inputs({values, onChange}) {
  return <div className="inputs-grid">{values.map((value, i) =>
    <label className="input-row" key={i}><span>x<sub>{i + 1}</sub></span>
      <input aria-label={'Input ' + (i + 1)} type="range" min="0" max="1" step="0.01"
        value={value === '' ? 0 : value} onChange={e => onChange(values.map((v, j) => j === i ? +e.target.value : v))}/>
      <input aria-label={'Input ' + (i + 1) + ' value'} type="number" min="0" max="1" step="0.01"
        value={value} onChange={e => onChange(values.map((v, j) => j === i ? e.target.value : v))}/>
    </label>)}</div>;
}

function RunDetails({record}) {
  return <p className="run-details">Computed with {record.engine} · engine {record.engine_version}
    <br/>{new Date(record.created_at).toLocaleString()} · settings included in JSON</p>;
}

function FigurePreview({figure, close}) {
  const dialog = useRef(null);
  useEffect(() => { dialog.current.showModal(); }, []);
  return <dialog ref={dialog} className="figure-preview" onCancel={close}>
    <div className="panel-heading"><h2>{figure.title}</h2><button autoFocus onClick={close} aria-label="Close figure">Close ×</button></div>
    <img src={base + 'evidence/' + figure.file} alt={figure.title}/>
    <a href={base + 'evidence/' + figure.file} download>Download figure ↓</a>
  </dialog>;
}

function App() {
  const [view, setView] = useState(currentView);
  const [settings, setSettings] = useState(initialSettings);
  const [links, setLinks] = useState({forum: base + 'docs/community/index.html', chat: ''});
  const [records, setRecords] = useState({});
  const [busy, setBusy] = useState(false), [error, setError] = useState(''), [notice, setNotice] = useState('');
  const [status, setStatus] = useState('Ready to run');
  const [evidence, setEvidence] = useState(null), [archiveError, setArchiveError] = useState('');
  const [filter, setFilter] = useState('All'), [figure, setFigure] = useState(null);
  const [lab, setLab] = useState({kind: 'mzm', v_pi: 1, bias: Math.PI / 2, power_mw: 1, rin_db_hz: -150});
  const fileInput = useRef(null);
  const operation = useRef(false);
  const result = records.infer?.result, batch = records.batch?.result, neuron = records.neuron?.result, curve = records.component?.result;

  useEffect(() => {
    let active = true, unsubscribe = () => {}, removeNavigation = () => {};
    engine.then(module => { if (active) unsubscribe = module.engineStatus(setStatus); }).catch(e => setError(e.message));
    platform.then(module => { if (active) removeNavigation = module.installNavigation(e => setError(e.message || String(e))); });
    import(/* @vite-ignore */ base + 'community-config.js').then(module => module.getCommunityLinks())
      .then(value => { if (active) setLinks({forum: value.forum || base + 'docs/community/index.html', chat: value.chat}); });
    const changeView = () => { setView(currentView()); setError(''); setNotice(''); };
    window.addEventListener('hashchange', changeView);
    return () => { active = false; unsubscribe(); removeNavigation(); window.removeEventListener('hashchange', changeView); };
  }, []);

  useEffect(() => { loadEvidence(); }, []);
  async function loadEvidence() {
    setArchiveError('');
    try {
      const response = await fetch(base + 'evidence/catalog.json');
      if (!response.ok) throw new Error('The evidence catalogue is unavailable.');
      const data = await response.json();
      if (!Array.isArray(data) || data.some(item => typeof item.file !== 'string' || !/^[a-zA-Z0-9_-]+\.png$/.test(item.file)))
        throw new Error('The evidence catalogue is invalid.');
      setEvidence(data);
    } catch (e) { setArchiveError(e.message); }
  }
  const clearMessage = () => { setError(''); setNotice(''); };
  function updateSettings(patch) {
    setSettings(value => ({...value, ...patch}));
    setRecords(value => ({component: value.component}));
    clearMessage();
  }
  function updateLab(patch) {
    setLab(value => ({...value, ...patch}));
    setRecords(value => ({...value, component: undefined}));
    clearMessage();
  }
  async function action(task) {
    if (operation.current) return;
    operation.current = true; setBusy(true); clearMessage();
    try { await task(); } catch (e) { setError(e.message || String(e)); }
    finally { operation.current = false; setBusy(false); }
  }
  const annParameters = () => ({network: parseNetwork(settings.network), dac_bits: settings.dac_bits, adc_bits: settings.adc_bits});
  const annSettings = () => ({inputs: validateInputs(settings.inputs), ...annParameters()});
  function simulate(kind) {
    action(async () => {
      let request;
      if (kind === 'infer') request = {action: kind, ...annSettings()};
      else if (kind === 'batch') request = {action: kind, count: 100, seed: 12345, ...annParameters()};
      else if (kind === 'neuron') request = {action: kind, inputs: validateInputs(settings.inputs),
        dac_bits: settings.dac_bits, adc_bits: settings.adc_bits, weights: [0.8, -0.6, 0.4, -0.9], bias: 0.2};
      else request = lab.kind === 'mzm' ? {action: kind, kind: lab.kind,
        v_pi: numberInRange(lab.v_pi, 'Half-wave voltage', 0.1, 10), bias: numberInRange(lab.bias, 'Bias phase', -2 * Math.PI, 2 * Math.PI)}
        : {action: kind, kind: lab.kind, power_mw: numberInRange(lab.power_mw, 'Optical power', 0.01, 100),
          rin_db_hz: numberInRange(lab.rin_db_hz, 'RIN density', -180, -140), linewidth_hz: 1e6, seed: 1};
      setRecords(value => ({...value, [kind]: undefined}));
      const module = await engine;
      const meta = await module.execute({action: 'meta'});
      const computed = await module.execute(request);
      const record = {schema: 'prabha.run.v1', studio_version: version, engine_version: meta.version,
        engine: module.engineMode(), created_at: new Date().toISOString(), request, result: computed};
      setRecords(value => ({...value, [kind]: record}));
    });
  }
  async function save(name, content, type) {
    const saved = await (await platform).saveText(name, content, type);
    setNotice(saved ? 'Export ready: ' + name : 'Export cancelled.');
  }
  const exportRun = kind => action(() => save('prabha-' + kind + '.json', JSON.stringify(records[kind], null, 2)));
  const exportSettings = () => action(() => save('prabha-ann-settings.json',
    JSON.stringify({schema: 'prabha.ann-settings.v1', studio_version: version, settings: annSettings()}, null, 2)));
  function importSettings(event) {
    const file = event.target.files[0];
    event.target.value = '';
    if (!file) return;
    action(async () => {
      if (file.size > 256 * 1024) throw new Error('ANN imports must be smaller than 256 KB.');
      const value = importAnn(await file.text());
      updateSettings({...value, network: JSON.stringify(value.network, null, 2)});
      setNotice('ANN settings imported. Run a new simulation to compute results.');
    });
  }
  function resetReference() {
    setSettings(initialSettings());
    setRecords(value => ({component: value.component}));
    clearMessage();
  }
  let reference = false;
  try { reference = isReference(annParameters()); } catch { /* The editor can contain unfinished JSON. */ }

  return <div className="app-shell">
    <a className="skip-link" href="#workspace" onClick={event => {
      event.preventDefault(); document.getElementById('workspace').focus();
    }}>Skip to workspace</a>
    <aside className="sidebar">
      <a className="brand" href="#start"><img src={base + 'favicon.svg'} alt=""/><span>Prabha<small>PHOTONIC COMPUTING</small></span></a>
      <div className="section-caption">WORKSPACE</div>
      <nav aria-label="Workspace">{nav.map(([key, title, icon]) =>
        <a key={key} href={'#' + key} className={view === key ? 'active' : ''} aria-current={view === key ? 'page' : undefined}>
          <span className="nav-symbol" aria-hidden="true">{icon}</span>{title}</a>)}
        <a href={base + 'designer.html'}><span className="nav-symbol" aria-hidden="true">⌘</span>Component designer <span className="out">↗</span></a>
      </nav>
      <div className="section-caption">PROJECT</div>
      <nav aria-label="Project">
        <a href={base + 'docs/index.html'}>Documentation ↗</a>
        <a href={links.forum} target="_blank" rel="noreferrer">Community forum ↗</a>
        {links.chat && <a href={links.chat} target="_blank" rel="noreferrer">Discord chat ↗</a>}
        <a href={base + 'prabha-source.zip'} download>Download source ↓</a>
      </nav>
      <div className="sidebar-bottom"><span className="preview-dot"/>{version}<small>Open photonic-electronic simulation</small></div>
    </aside>
    <main id="workspace" tabIndex="-1">
      <header className="topbar"><span>Studio <span className="slash">/</span>{nav.find(item => item[0] === view)?.[1]}</span>
        <span className="engine-status" role="status"><i className={busy ? 'pulse' : ''}/>{status}</span></header>
      <div className="content">
        <div className="page-heading"><div><div className="eyebrow">PRABHA STUDIO · V0.1 PREVIEW</div>
          <h1>{headings[view][0]}</h1><p>{headings[view][1]}</p></div><span className="scope-label">Behavioural simulation</span></div>
        {error && <div role="alert" className="error">{error} <a href={base + 'docs/troubleshooting/index.html'}>Troubleshooting ↗</a></div>}
        {notice && <div role="status" className="notice">{notice}</div>}

        {view === 'start' && <>
          <section className="welcome-grid">
            <div className="welcome-copy"><span className="eyebrow">YOUR FIRST EXPERIMENT</span><h2>A small network.<br/>Every stage visible.</h2>
              <p>Start with four inputs and a fixed 4–3–2 ANN. Inspect the neuron chain, compare outputs and export the settings behind your result.</p>
              <div className="button-row"><a className="primary" href="#ann">Open ANN workspace →</a><a className="secondary" href={base + 'docs/quickstart/index.html'}>Read the quick start</a></div>
              <p className="hint">No account is needed. The hosted preview downloads Python on your first run; computation then runs in this browser.</p>
            </div>
            <div className="welcome-graph"><Network inputs={DEFAULT_INPUTS}/><span className="small muted">Optical weighting · electronic integration · digital readout</span></div>
          </section>
          <div className="section-heading"><h2>Explore the prototype</h2><span className="muted small">Models, evidence and people</span></div>
          <div className="feature-grid">
            {[['01', 'Reproduce the baseline', 'Keep the reference network and 12-bit converters. Validate 100 inputs with seed 12345.', '#ann', 'Run the ANN'],
              ['02', 'Inspect a neuron', 'Follow signed products, balanced current, capacitor voltage and activation.', '#neuron', 'View the trace'],
              ['03', 'Explore components', 'Generate an MZM transfer curve or a seeded laser power waveform.', '#components', 'Open the lab'],
              ['04', 'Compare the evidence', 'Browse 25 saved figures and four datasets from the original experiments.', '#evidence', 'Browse the archive']].map(([n, title, text, href, cta]) =>
              <article className="feature-card" key={n}><span className="card-number">{n}</span><h3>{title}</h3><p>{text}</p><a href={href}>{cta} →</a></article>)}
          </div>
          <section className="baseline-card"><div><div className="eyebrow">ARCHIVED REFERENCE · 100 INPUTS</div><h2>Numerical agreement you can reproduce</h2></div>
            <div className="metric-strip"><div><span>Output RMS error</span><strong>7.8644 × 10⁻⁵</strong></div><div><span>Maximum error</span><strong>1.7828 × 10⁻⁴</strong></div><div><span>Ordering mismatches</span><strong>0 / 100</strong></div></div>
            <p className="hint">Fixed weights, 12-bit DAC/ADC, seed 12345. These results measure agreement with an analytical model; they do not measure task accuracy, speed or energy.</p>
          </section>
          <div className="community-grid">
            <section><h2>Build Prabha with us</h2><p>Ask detailed questions, share reproducible experiments and discuss development in the forum. Use Discord for quick conversations.</p>
              <div className="button-row"><a href={links.forum} target="_blank" rel="noreferrer">Visit the forum ↗</a>{links.chat && <a href={links.chat} target="_blank" rel="noreferrer">Join Discord ↗</a>}</div></section>
            <section><h2>Run locally or build desktop</h2><p>The web preview is available now. Windows, macOS and Linux packaging is prepared for native build and installation checks.</p>
              <a href={base + 'docs/desktop/index.html'}>Desktop build guide →</a><p className="small muted">CNN primitives and LLM evaluation are planned work.</p></section>
          </div>
        </>}

        {(view === 'ann' || view === 'neuron') && <>
          <div className="workspace-toolbar"><span className={'run-badge ' + (reference ? '' : 'exploratory')}>
            {view === 'neuron' ? 'Fixed reference neuron' : reference ? 'Reference network · 12-bit converters' : 'Exploratory configuration'}</span>
            {view === 'ann' && <div className="button-row">
              <button className="text-button" disabled={busy} onClick={() => fileInput.current.click()}>Import ANN JSON ↑</button>
              <input type="file" accept=".json,application/json" hidden ref={fileInput} onChange={importSettings} aria-label="Import ANN JSON"/>
              <button className="text-button" disabled={busy} onClick={exportSettings}>Export settings ↓</button>
              <button className="text-button" disabled={busy} onClick={resetReference}>Reset reference</button>
            </div>}
          </div>
          <div className="work-grid">
            <fieldset className="controls" disabled={busy}><div className="panel-heading"><h2>Input signals</h2>
              <button className="text-button" onClick={() => updateSettings({inputs: [...DEFAULT_INPUTS]})}>Reset inputs</button></div>
              <p className="muted small">Normalized amplitude, 0 to 1</p>
              <Inputs values={settings.inputs} onChange={inputs => updateSettings({inputs})}/>
              <div className="divider"/><h3>Converter resolution</h3>
              <div className="field-pair">{[['dac_bits', 'DAC'], ['adc_bits', 'ADC']].map(([key, label]) =>
                <label key={key}>{label}<select value={settings[key]} onChange={e => updateSettings({[key]: +e.target.value})}>
                  {PRECISIONS.map(value => <option key={value} value={value}>{value} bits</option>)}</select></label>)}</div>
              <p className="hint">Changing settings clears previous results. Keep 12 bits to reproduce the archived reference.</p>
              <button className="primary" onClick={() => simulate(view === 'ann' ? 'infer' : 'neuron')}>{busy ? 'Running…' : view === 'ann' ? 'Run inference' : 'Run neuron'} ↗</button>
              {view === 'ann' && <><button className="secondary" onClick={() => simulate('batch')}>Validate 100 inputs</button>
                <p className="hint">Batch: seed 12345, 100 sampled inputs. Uses your network and converters; ignores the four input sliders.</p></>}
              <div className="model-spec">1 mW source · 1 pF capacitor<br/>1 ns integration · sigmoid activation</div>
            </fieldset>
            <section className="results" aria-busy={busy}><div className="panel-heading"><h2>{view === 'ann' ? 'Network propagation' : 'Computation trace'}</h2>
              <span className="muted small">{view === 'ann' ? '4 → 3 → 2' : '4 signed products · 1 output'}</span></div>
              {view === 'ann' ? <>
                <Network inputs={result?.inputs || settings.inputs.map(v => v === '' ? null : Number(v))} result={result}/>
                {!result && <p className="empty-note">Run inference to inspect computed values for the current settings.</p>}
                {result && <><div className="metric-strip"><div><span>Maximum error</span><strong>{sci(result.max_error)}</strong></div><div><span>RMS error</span><strong>{sci(result.rms_error)}</strong></div></div>
                  <table><thead><tr><th>Output</th><th>Analytical</th><th>Physical model</th><th>Difference</th></tr></thead><tbody>
                    {result.physical_output.map((v, i) => <tr key={i}><td>y<sub>{i + 1}</sub></td><td>{fmt(result.ideal_output[i])}</td><td className="teal">{fmt(v)}</td><td>{sci(result.error[i])}</td></tr>)}
                  </tbody></table><RunDetails record={records.infer}/><button className="text-button" disabled={busy} onClick={() => exportRun('infer')}>Export inference JSON ↓</button></>}
              </> : neuron ? <>
                <table><thead><tr><th>Channel</th><th>Ideal xw</th><th>Recovered xw</th><th>Current (A)</th></tr></thead>
                  <tbody>{neuron.products.map((v, i) => <tr key={i}><td>{i + 1}</td><td>{fmt(neuron.ideal_products[i])}</td><td>{fmt(v)}</td><td>{sci(neuron.differential_current_A[i])}</td></tr>)}</tbody></table>
                <dl className="trace">{[['Capacitor voltage', neuron.capacitor_voltage_V, 'V'], ['Pre-activation', neuron.pre_activation, ''],
                  ['Analog sigmoid', neuron.analog_activation, ''], ['ADC code', neuron.adc_code, ''], ['Digital output', neuron.output, ''],
                  ['Reference output', neuron.ideal, '']].map(([label, value, unit]) =>
                  <div key={label}><dt>{label}</dt><dd>{fmt(value, label === 'ADC code' ? 0 : 9)} {unit}</dd></div>)}</dl>
                <RunDetails record={records.neuron}/><button className="text-button" disabled={busy} onClick={() => exportRun('neuron')}>Export neuron JSON ↓</button>
              </> : <div className="empty-state"><span>Σ xᵢwᵢ + θ</span><h3>Signed optical products, explicit electronic stages</h3>
                <p>Weights: [0.8, −0.6, 0.4, −0.9]. Bias: 0.2. Run the neuron to inspect every stage.</p></div>}
            </section>
          </div>
          {view === 'ann' && <details className="network-editor"><summary>Network weights and biases <span>Fixed 4 → 3 → 2 architecture</span></summary>
            <p className="muted">Weights: [−1, 1]. Biases: [−10, 10]. Custom values are exploratory.</p>
            <textarea aria-label="Network JSON" value={settings.network} disabled={busy} onChange={e => updateSettings({network: e.target.value})} spellCheck={false}/>
            <button className="text-button" disabled={busy} onClick={() => updateSettings({network: JSON.stringify(DEFAULT_NETWORK, null, 2)})}>Restore reference network</button></details>}
          {view === 'ann' && batch && <section className="batch-section" aria-label="Batch validation">
            <div className="panel-heading"><h2>Batch validation</h2><div className="button-row">
              <button className="text-button" disabled={busy} onClick={() => exportRun('batch')}>Export batch JSON ↓</button>
              <button className="text-button" disabled={busy} onClick={() => action(() => save('prabha-batch.csv', batchCsv(records.batch), 'text/csv'))}>Export CSV ↓</button></div></div>
            <div className="metric-strip"><div><span>Output RMS</span><strong>{sci(batch.rms_error)}</strong></div><div><span>Maximum error</span><strong>{sci(batch.max_error)}</strong></div><div><span>Ordering mismatches</span><strong>{batch.winner_mismatches}/{batch.count}</strong></div></div>
            <LineChart x={batch.rows.map(row => row.sample)} y={batch.rows.map(row => Math.max(...row.error.map(Math.abs)))} xLabel="Input sample" yLabel="Maximum absolute output error"/>
            <p className="hint">{isReference(records.batch.request) ? 'Reference configuration.' : 'Exploratory configuration.'} Seed {batch.seed}. Output ordering is not classification accuracy. Keep the JSON alongside CSV for the full network settings.</p>
            <RunDetails record={records.batch}/>
          </section>}
          <p className="scope-note">This ANN includes converter quantization and behavioural activation. Laser RIN, detector noise and receiver bandwidth are studied separately in the archive.</p>
        </>}

        {view === 'components' && <>
          <div className="work-grid"><fieldset className="controls" disabled={busy}><h2>Live experiment</h2>
            <label>Component<select value={lab.kind} onChange={e => updateLab({kind: e.target.value})}><option value="mzm">Mach–Zehnder modulator</option><option value="laser">CW laser with noise</option></select></label>
            {(lab.kind === 'mzm' ? [['v_pi', 'Half-wave voltage, Vπ (V)', 0.1, 10, 0.1], ['bias', 'Bias phase (rad)', -2 * Math.PI, 2 * Math.PI, 0.1]]
              : [['power_mw', 'Mean optical power (mW)', 0.01, 100, 0.1], ['rin_db_hz', 'RIN density (dB/Hz)', -180, -140, 1]]).map(([key, label, min, max, step]) =>
              <label key={key}>{label}<input type="number" min={min} max={max} step={step} value={lab[key]} onChange={e => updateLab({[key]: e.target.value})}/></label>)}
            {lab.kind === 'mzm' ? <p className="formula">T(V) = cos²(πV / 2Vπ + φᵦ / 2)</p> :
              <p className="hint">160 GHz sampling, 10 ns duration, 1 MHz linewidth, seed 1. Bounded Gaussian RIN approximation.</p>}
            <button className="primary" onClick={() => simulate('component')}>{busy ? 'Running…' : 'Run experiment'} ↗</button>
          </fieldset><section className="results"><h2>{lab.kind === 'mzm' ? 'Optical transfer' : 'Optical power waveform'}</h2>
            {curve ? <><LineChart x={curve.x} y={curve.y} xLabel={curve.x_label} yLabel={curve.y_label}/>
              <dl className="trace">{Object.entries(curve.summary).map(([key, value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{sci(value)}</dd></div>)}</dl>
              <RunDetails record={records.component}/><button className="text-button" disabled={busy} onClick={() => exportRun('component')}>Export experiment JSON ↓</button>
            </> : <div className="empty-state"><span>{lab.kind === 'mzm' ? 'cos²' : 'E(t)'}</span><p>Run the experiment to generate a response from the Python model.</p></div>}
          </section></div>
          <section className="plain-section"><h2>More component evidence</h2><div className="component-list">
            {[['CW laser', 'Power, wavelength, RIN, linewidth and seeds'], ['MZM', 'Transfer, local linearity and inverse encoding'],
              ['Photodetector', 'Responsivity, dark current and shot noise'], ['DAC and ADC', 'Code boundaries and resolution sweeps'],
              ['Transimpedance amplifier', 'Gain, finite bandwidth and input noise'], ['Capacitor and activation', 'Charge, gain, bias and sigmoid']].map(([title, text]) =>
              <div key={title}><h3>{title}</h3><p>{text}</p></div>)}</div><a href="#evidence">Explore saved validation evidence →</a></section>
        </>}

        {view === 'evidence' && <>
          {archiveError ? <div role="alert" className="error">{archiveError} <button onClick={loadEvidence}>Retry catalogue</button></div> : !evidence ? <p role="status">Loading evidence…</p> : <>
            <div className="archive-top"><span>{evidence.length} saved figures · 47 nonempty experiment files · 4 datasets</span>
              <label className="inline-label">Filter<select value={filter} onChange={e => setFilter(e.target.value)}>{['All', ...new Set(evidence.map(item => item.group))].map(item => <option key={item}>{item}</option>)}</select></label></div>
            <div className="evidence-grid">{evidence.filter(item => filter === 'All' || item.group === filter).map(item =>
              <article key={item.file}><button className="figure-button" onClick={() => setFigure(item)} aria-label={'Enlarge ' + item.title}>
                <img src={base + 'evidence/' + item.file} alt={item.title} loading="lazy"/></button>
                <div><small>{item.group}</small><h3>{item.title}</h3><p>Archived simulation evidence</p><a href={base + 'evidence/' + item.file} download>Download figure ↓</a></div></article>)}</div>
          </>}
          <section className="plain-section"><h2>Original numerical datasets</h2>
            {['ann_batch_validation.csv', 'dac_adc_resolution_matrix.csv', 'full_chain_monte_carlo.csv', 'photodetector_shot_noise_power_sweep.csv'].map(file =>
              <p key={file}><a href={base + 'evidence/' + file} download>{file.replaceAll('_', ' ')} ↓</a></p>)}
          </section>
        </>}
        <footer><span>Prabha · Abhishek Singh · IIT Patna · {version}</span><a href={base + 'docs/model-scope/index.html'}>Model scope and reproducibility ↗</a></footer>
      </div>
    </main>
    {figure && <FigurePreview figure={figure} close={() => setFigure(null)}/>}
  </div>;
}

createRoot(document.getElementById('root')).render(<App/>);
