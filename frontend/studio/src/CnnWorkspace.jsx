import React, {useEffect, useRef, useState} from 'react';
import {version} from '../package.json';
import {validateSettings, parseExperimentFile, settingsDocument, resultsCsv} from '../public/cnn-settings.js';
import './cnn.css';

const STAGES = [
  ['input', 'Input', '1 × 8 × 8'], ['convolution', 'Cross-corr + bias', '4 × 6 × 6'],
  ['relu', 'ReLU', '4 × 6 × 6'], ['pool', 'Max pool', '4 × 3 × 3'],
  ['flatten', 'Flatten', '36 features'], ['logits', 'Logits', '10 classes']
];
const sci = value => Number.isFinite(value) ? value.toExponential(4) : '—';
const clone = value => JSON.parse(JSON.stringify(value));
const pixelText = pixels => '[\n' + pixels.map(row => '  ' + JSON.stringify(row)).join(',\n') + '\n]';

function Digit({pixels, editable = false, onPaint, disabled = false}) {
  return <div className={'cnn-digit' + (editable ? ' editable' : '')}
    role={editable ? 'group' : 'img'} aria-label={editable ? 'Editable digit pixels' : 'Selected digit image'}>
    {pixels.flatMap((row, r) => row.map((value, c) => {
      const gray = Math.round(value / 16 * 255), style = {background: `rgb(${gray} ${gray} ${gray})`};
      return editable ? <button type="button" key={r * 8 + c} style={style} disabled={disabled}
        aria-label={`Pixel row ${r + 1} column ${c + 1}, value ${value}`}
        onClick={() => onPaint(r, c)}/> : <span key={r * 8 + c} style={style}/>;
    }))}
  </div>;
}

function Heatmap({matrix, low, high, label}) {
  const ref = useRef(null);
  useEffect(() => {
    const canvas = ref.current;
    canvas.width = matrix[0].length; canvas.height = matrix.length;
    const context = canvas.getContext('2d'), image = context.createImageData(canvas.width, canvas.height);
    matrix.flat().forEach((value, i) => {
      const t = Math.max(0, Math.min(1, (value - low) / (high - low || 1)));
      image.data.set([Math.round(35 + 200 * t), Math.round(53 + 165 * t), Math.round(65 + 105 * t), 255], i * 4);
    });
    context.putImageData(image, 0, 0);
  }, [matrix, low, high]);
  return <figure><figcaption>{label}</figcaption><canvas ref={ref} role="img" aria-label={label + ' layer heatmap'}
    style={{aspectRatio: `${matrix[0].length} / ${matrix.length}`}}/></figure>;
}

function plane(values, channel) {
  if (!Array.isArray(values[0])) return [values];
  return Array.isArray(values[0][0]) ? values[channel] : values;
}

function Precision({label, value, onChange}) {
  return <label>{label}<select value={value === null ? 'off' : value} onChange={event => onChange(event.target.value === 'off' ? null : Number(event.target.value))}>
    <option value="off">Off</option>{Array.from({length: 24}, (_, i) => <option key={i + 1} value={i + 1}>{i + 1} bits</option>)}
  </select></label>;
}

export default function CnnWorkspace({active, engine, platform, busy, runTask, onSettingsChange}) {
  const [info, setInfo] = useState(null), [settings, setSettings] = useState(null);
  const [pixelsText, setPixelsText] = useState(''), [modelText, setModelText] = useState('');
  const [record, setRecord] = useState(null), [inspection, setInspection] = useState(null);
  const [execution, setExecution] = useState('auto'), [benchmark, setBenchmark] = useState(null);
  const [selected, setSelected] = useState(0), [stage, setStage] = useState('input'), [channel, setChannel] = useState(0);
  const [brush, setBrush] = useState('16'), [sampleIndex, setSampleIndex] = useState('0');
  const [message, setMessage] = useState('Loading the trained CNN…');
  const fileInput = useRef(null), started = useRef(false), current = useRef(null);
  const inspectionCache = useRef(new Map()), ticket = useRef(0);

  function apply(value) {
    const accepted = validateSettings(value);
    setSettings(accepted); setPixelsText(pixelText(accepted.input.pixels));
    setModelText(JSON.stringify(accepted.model, null, 2));
  }
  function invalidate(text = 'Settings changed. Run inference for fresh results.') {
    current.current = null; ticket.current++; inspectionCache.current.clear();
    setRecord(null); setInspection(null); setBenchmark(null); setSelected(0); setMessage(text); onSettingsChange();
  }
  function edit(section, patch) {
    setSettings(value => ({...value, [section]: {...value[section], ...patch}}));
    invalidate();
  }
  function read() {
    let pixels, model;
    try { pixels = JSON.parse(pixelsText); } catch { throw new Error('Pixel JSON must contain eight rows of eight numbers.'); }
    try { model = JSON.parse(modelText); } catch { throw new Error('Weights JSON is invalid. Check commas and brackets.'); }
    const input = settings.input;
    if (input.mode === 'heldout' && (String(input.count).trim() === '' || String(input.start).trim() === ''))
      throw new Error('Start index and image count are required.');
    if (String(settings.converters.adc_full_scale).trim() === '') throw new Error('ADC range is required.');
    return validateSettings({input: {...input, pixels, count: input.mode === 'custom' ? 1 : Number(input.count),
      start: input.mode === 'custom' ? 0 : Number(input.start), label: input.label === '' || input.label === null ? null : Number(input.label)},
      model, converters: {...settings.converters, adc_full_scale: Number(settings.converters.adc_full_scale)}});
  }
  function initialize() {
    return runTask(async () => {
      const loaded = await (await engine).execute({action: 'cnn_info'});
      setInfo(loaded); apply(loaded.default_settings);
      setMessage('Trained checkpoint ready. Run inference or validate all 360 held-out images.');
    });
  }
  useEffect(() => {
    if (active && !started.current) { started.current = true; initialize(); }
  }, [active]);

  function run(fullBatch = false) {
    runTask(async () => {
      const snapshot = read();
      if (fullBatch) {
        snapshot.input = {...snapshot.input, mode: 'heldout', start: 0, count: 360};
        apply(snapshot);
      }
      invalidate('Computing fresh NumPy and Prabha inference…');
      try {
        const module = await engine, meta = await module.execute({action: 'meta'});
        const result = await module.execute({action: 'cnn', settings: snapshot, execution});
        const next = {schema: 'prabha.cnn-run.v3', execution, studio_version: version, engine: module.engineMode(),
          engine_version: meta.version, created_at: new Date().toISOString(), settings: result.settings, result};
        current.current = next; setRecord(next); setSelected(0);
        const first = {...result.inspection, index: 0, label: result.rows[0].label,
          test_position: result.rows[0].test_position, settings: result.settings};
        inspectionCache.current.set(0, first); setInspection(first);
        setMessage(result.labelled_images ? `Complete: NumPy ${result.numpy_correct}/${result.labelled_images}, Prabha ${result.prabha_correct}/${result.labelled_images} correct.`
          : 'Complete: predictions computed for an unlabelled image.');
      } catch (error) { setMessage('Inference failed. Correct the settings and run again.'); throw error; }
    });
  }
  function selectSample(index) {
    runTask(async () => {
      const snapshot = current.current;
      if (!snapshot) return;
      const id = ++ticket.current;
      setSelected(index); setInspection(null);
      const value = inspectionCache.current.get(index) || await (await engine).execute({action: 'cnn_inspect', settings: snapshot.settings, execution: snapshot.execution, index});
      if (current.current !== snapshot || ticket.current !== id) return;
      inspectionCache.current.set(index, value); setInspection(value);
    });
  }
  async function save(name, text, mime = 'application/json') {
    const saved = await (await platform).saveText(name, text, mime);
    setMessage(saved ? 'Export ready: ' + name : 'Export cancelled.');
  }
  function exportSettings() {
    runTask(async () => {
      const value = await (await engine).execute({action: 'cnn_validate', settings: read()});
      await save('prabha-cnn-settings.json', JSON.stringify({...settingsDocument(value.settings, execution), studio_version: version}, null, 2));
    });
  }
  function importSettings(event) {
    const file = event.target.files?.[0]; event.target.value = '';
    if (!file) return;
    runTask(async () => {
      if (file.size > 1_000_000) throw new Error('CNN settings imports must be smaller than 1 MB.');
      const value = parseExperimentFile(await file.text());
      const accepted = await (await engine).execute({action: 'cnn_validate', settings: value.settings, execution: value.execution});
      apply(accepted.settings); setExecution(value.execution); invalidate('CNN settings imported. Run inference to compute fresh results.');
    });
  }
  function paint(row, column) {
    runTask(async () => {
      const value = Number(brush);
      if (!brush.trim() || !Number.isFinite(value) || value < 0 || value > 16) throw new Error('Brush must be between 0 and 16.');
      const pixels = JSON.parse(pixelsText), input = settings.input;
      const checked = validateSettings({...info.default_settings, input: {...info.default_settings.input, pixels}});
      checked.input.pixels[row][column] = value;
      setPixelsText(pixelText(checked.input.pixels)); edit('input', {...input, pixels: checked.input.pixels, mode: 'custom'});
    });
  }

  if (!info || !settings) return <section className="results cnn-loading" aria-busy={busy}>
    <h2>Trained CNN</h2><p className="muted">{message}</p>
    {!busy && <button className="secondary" onClick={initialize}>Load CNN workspace</button>}
  </section>;

  const result = record?.result, row = result?.rows[selected];
  const layer = inspection?.layers.find(value => value.name === stage);
  const channels = layer?.shape.length === 3 ? layer.shape[0] : 1;
  const shownChannel = Math.min(channel, channels - 1);
  const a = layer ? plane(layer.numpy, shownChannel) : null, b = layer ? plane(layer.prabha, shownChannel) : null;
  const difference = a?.map((values, r) => values.map((value, c) => b[r][c] - value));
  let preview = settings.input.pixels;
  try { preview = validateSettings({...info.default_settings, input: {...info.default_settings.input, pixels: JSON.parse(pixelsText)}}).input.pixels; } catch { /* Keep incomplete edits visible. */ }
  const editedWeights = modelText !== JSON.stringify(info.default_settings.model, null, 2);

  return <div className="cnn-workspace">
    <div className="workspace-toolbar"><span className={'run-badge ' + (editedWeights ? 'exploratory' : '')}>
      {editedWeights ? 'Editable CNN weights' : 'Trained checkpoint · 410 parameters'}</span>
      <div className="button-row">
        <button className="text-button" disabled={busy} onClick={() => fileInput.current.click()}>Import CNN JSON ↑</button>
        <input type="file" accept=".json,application/json" ref={fileInput} hidden aria-label="Import CNN JSON" onChange={importSettings}/>
        <button className="text-button" disabled={busy} onClick={exportSettings}>Export CNN settings ↓</button>
        <button className="text-button" disabled={busy} onClick={() => {apply(clone(info.default_settings)); setExecution('auto'); invalidate('Reference checkpoint and converters restored. Run for fresh results.');}}>Reset CNN reference</button>
      </div>
    </div>
    <div className="work-grid">
      <fieldset className="controls" disabled={busy}>
        <h2>Input image</h2>
        <label>Input source<select value={settings.input.mode} onChange={event => edit('input', {mode: event.target.value})}>
          <option value="heldout">Held-out digits</option><option value="custom">Editable 8 × 8 image</option>
        </select></label>
        {settings.input.mode === 'heldout' ? <div className="field-pair">
          <label>Start index (0-based)<input type="number" min="0" max="359" value={settings.input.start} onChange={event => edit('input', {start: event.target.value})}/></label>
          <label>Image count<input type="number" min="1" max="360" value={settings.input.count} onChange={event => edit('input', {count: event.target.value})}/></label>
        </div> : <>
          <Digit pixels={preview} editable disabled={busy} onPaint={paint}/>
          <div className="field-pair"><label>Pixel brush<input type="number" min="0" max="16" value={brush} onChange={event => setBrush(event.target.value)}/></label>
            <label>True digit (optional)<input type="number" min="0" max="9" value={settings.input.label ?? ''} onChange={event => edit('input', {label: event.target.value})}/></label></div>
          <label className="cnn-pixels">Pixel values (0–16)<textarea rows="10" spellCheck={false} aria-label="Editable pixel matrix" value={pixelsText}
            onChange={event => {setPixelsText(event.target.value); invalidate();}}/></label>
          <label>Digit index<input type="number" min="0" max="359" value={sampleIndex} onChange={event => setSampleIndex(event.target.value)}/></label>
          <button className="text-button" onClick={() => runTask(async () => {
            if (!sampleIndex.trim()) throw new Error('Digit index is required.');
            const loaded = await (await engine).execute({action: 'cnn_info', sample_index: Number(sampleIndex)});
            setPixelsText(pixelText(loaded.sample.pixels)); edit('input', {pixels: loaded.sample.pixels, label: loaded.sample.label});
          })}>Load held-out digit for editing</button>
        </>}
        <div className="divider"/><h3>Execution</h3>
        <label>Physical execution<select value={execution} onChange={event => {setExecution(event.target.value); invalidate();}}>
          <option value="auto">Automatic</option><option value="symbol">Fast constant-symbol</option>
          <option value="waveform">Sampled waveform</option>
        </select></label>
        <p className="hint">Fast mode integrates constant, noiseless symbols and retains the converter settings. Sampled mode evaluates every time sample.</p>
        <h3>Converter resolution</h3>
        <div className="field-pair">
          <Precision label="Input DAC" value={settings.converters.dac_bits} onChange={value => edit('converters', {dac_bits: value})}/>
          <Precision label="MAC output ADC" value={settings.converters.adc_bits} onChange={value => edit('converters', {adc_bits: value})}/>
        </div>
        <label>ADC ± range (V)<input type="number" min="0.001" max="1000000" step="any" value={settings.converters.adc_full_scale}
          onChange={event => edit('converters', {adc_full_scale: event.target.value})}/></label>
        <label>DAC tie rule<select value={settings.converters.dac_rounding} onChange={event => edit('converters', {dac_rounding: event.target.value})}>
          <option value="nearest_lower">Lower code at a tie</option><option value="nearest_even">Nearest even</option></select></label>
        <p className="hint">ADC conversion precedes inverse scaling and digital bias. Values outside its range raise an error.</p>
        <button className="primary" onClick={() => run()}>{busy ? 'Running…' : 'Run CNN inference'} ↗</button>
        <button className="secondary" onClick={() => run(true)}>Validate 360 images</button>
        <button className="secondary" onClick={() => runTask(async () => {
          setMessage('Benchmarking both physical modes and NumPy, with three measured repetitions…');
          const measured = await (await engine).execute({action: 'cnn_benchmark', settings: read(), blocks: 3, warmups: 1});
          setBenchmark(measured); setMessage('Benchmark complete. The selected workload and timing scope are included in the export.');
        })}>Benchmark both modes</button>
        <button className="text-button cnn-validate" onClick={() => runTask(async () => {
          await (await engine).execute({action: 'cnn_validate', settings: read()}); setMessage('CNN settings valid. Run inference to compute predictions.');
        })}>Validate CNN settings</button>
        <p className="model-spec">1 mW source · 1 pF capacitor<br/>16 GHz sampling · noise off</p>
      </fieldset>
      <section className="results" aria-busy={busy} aria-label="CNN results">
        <div className="panel-heading"><h2>Network propagation</h2><span className="muted small">8 × 8 → 10 classes</span></div>
        <div className="cnn-stages" aria-label="CNN stages">{STAGES.map(([name, title, shape]) => <button key={name}
          className={stage === name ? 'active' : ''} disabled={busy} aria-pressed={stage === name}
          onClick={() => {setStage(name); setChannel(0);}}><strong>{title}</strong><span>{shape}</span>
          {inspection && <small>Δ {sci(inspection.layers.find(value => value.name === name)?.maximum_error)}</small>}</button>)}</div>
        <p className="cnn-status" role="status">{message}</p>
        {!result ? <div className="empty-state"><span>Conv → ReLU → Pool → Dense</span><h3>One checkpoint, two inference paths</h3>
          <p>Run the current settings to compare NumPy and the Prabha component model, then inspect each stage. CNN Conv2D uses cross-correlation, without flipping the learned filter.</p>
          <p className="small">Archived reference: 354/360 correct (98.33%), zero prediction disagreements. Live results appear after a new run.</p></div> : <>
          <div className="metric-strip cnn-metrics">
            <div><span>NumPy accuracy</span><strong>{result.numpy_accuracy === null ? 'Unlabelled' : (100 * result.numpy_accuracy).toFixed(2) + '%'}</strong></div>
            <div><span>Prabha accuracy</span><strong>{result.prabha_accuracy === null ? 'Unlabelled' : (100 * result.prabha_accuracy).toFixed(2) + '%'}</strong></div>
            <div><span>Disagreements</span><strong>{result.prediction_disagreements}/{result.count}</strong></div>
          </div>
          <div className="cnn-summary"><Digit pixels={Array.from({length: 8}, (_, i) => row.pixels.slice(i * 8, i * 8 + 8))}/>
            <div><p className="small muted">{row.test_position === null ? 'Custom image' : `Test image ${row.test_position + 1}`} · True digit: {row.label ?? 'unlabelled'}</p>
              <div className="metric-strip"><div><span>NumPy prediction</span><strong>{row.numpy_prediction}</strong></div><div><span>Prabha prediction</span><strong>{row.prabha_prediction}</strong></div></div>
              <p className="hint">Maximum logit error: {sci(row.maximum_logit_error)}</p></div></div>
          <div className="button-row">
            <button className="text-button" disabled={busy} onClick={() => runTask(() => save('prabha-cnn-run.json', JSON.stringify(record, null, 2)))}>Export CNN run JSON ↓</button>
            <button className="text-button" disabled={busy} onClick={() => runTask(() => save('prabha-cnn-results.csv', resultsCsv(result), 'text/csv'))}>Export CNN CSV ↓</button>
          </div>
          <p className="run-details">Computed with {record.engine} · engine {record.engine_version}<br/>{new Date(record.created_at).toLocaleString()} · exact settings included in JSON</p>
        </>}
      </section>
    </div>
    <details className="network-editor cnn-weights"><summary>Convolution and dense weights <span>410 parameters · fixed architecture</span></summary>
      <p className="muted">conv_weight [4,1,3,3] · conv_bias [4] · dense_weight [10,36] · dense_bias [10]. Finite values from −100 to 100.</p>
      <textarea aria-label="Editable CNN weights and biases JSON" value={modelText} disabled={busy} spellCheck={false}
        onChange={event => {setModelText(event.target.value); invalidate();}}/>
      <button className="text-button" disabled={busy} onClick={() => {setModelText(JSON.stringify(info.default_settings.model, null, 2)); invalidate();}}>Restore trained weights only</button>
    </details>
    {result && <>
      <section className="cnn-panel" aria-label="CNN layer inspection">
        <div className="panel-heading"><h2>Layer inspection</h2><button className="text-button" disabled={busy || !inspection}
          onClick={() => runTask(() => save('prabha-cnn-layer.json', JSON.stringify({schema: 'prabha.cnn-layer.v1',
            created_at: record.created_at, engine: record.engine, engine_version: record.engine_version,
            settings: record.settings, selected_row: selected, selected_stage: stage, feature_channel: shownChannel, inspection}, null, 2)))}>Export layer inspection ↓</button></div>
        <fieldset disabled={busy} className="cnn-layer-controls field-pair">
          <label>Stage<select value={stage} onChange={event => {setStage(event.target.value); setChannel(0);}}>{STAGES.map(([key, title]) => <option key={key} value={key}>{title}</option>)}</select></label>
          <label>Feature channel<select value={shownChannel} onChange={event => setChannel(Number(event.target.value))}>{Array.from({length: channels}, (_, i) => <option key={i} value={i}>Channel {i}</option>)}</select></label>
        </fieldset>
        {layer ? <><p className="hint">Shape [{layer.shape.join(', ')}] · RMS error {sci(layer.rms_error)} · maximum error {sci(layer.maximum_error)}</p>
          <div className="cnn-heatmaps"><Heatmap matrix={a} low={Math.min(layer.numpy_min, layer.prabha_min)} high={Math.max(layer.numpy_max, layer.prabha_max)} label="NumPy"/>
            <Heatmap matrix={b} low={Math.min(layer.numpy_min, layer.prabha_min)} high={Math.max(layer.numpy_max, layer.prabha_max)} label="Prabha"/>
            <Heatmap matrix={difference} low={-layer.maximum_error} high={layer.maximum_error} label="Prabha minus NumPy"/></div>
          <details><summary>Exact tensor values for both paths</summary><pre>{JSON.stringify({shape: layer.shape, numpy: layer.numpy, prabha: layer.prabha}, null, 2)}</pre></details>
        </> : <p className="muted">Computing the selected image…</p>}
        <p className="hint">Both output maps share a colour range. The difference uses a symmetric range. First-image tensors come from the current run; other selected images are inspected outside inference timing.</p>
      </section>
      <section className="cnn-panel" aria-label="CNN predictions"><h2>Predictions</h2>
        <div className="cnn-table"><table><thead><tr><th>Test image</th><th>True digit</th><th>NumPy</th><th>Prabha</th><th>Result</th></tr></thead><tbody>
          {result.rows.map((item, i) => <tr key={i} className={i === selected ? 'cnn-selected' : ''}>
            <td><button disabled={busy} className="text-button" aria-pressed={i === selected} aria-label={'Inspect prediction ' + (i + 1)}
              onClick={() => selectSample(i)}>{item.test_position === null ? 'Custom' : item.test_position + 1}</button></td>
            <td>{item.label ?? '—'}</td><td>{item.numpy_prediction}</td><td>{item.prabha_prediction}</td>
            <td className={item.correct === false ? 'cnn-incorrect' : ''}>{item.correct === null ? 'Unlabelled' : item.correct ? 'Correct' : 'Incorrect'}</td></tr>)}
        </tbody></table></div>
        <p className="hint">Logit error: RMS {sci(result.rms_logit_error)} · maximum {sci(result.max_logit_error)}<br/>
          {result.mac_calls.toLocaleString()} MAC calls · {result.device_passes.toLocaleString()} device passes<br/>
          {result.equivalent_waveform_samples.toLocaleString()} equivalent samples · {result.materialized_waveform_samples.toLocaleString()} evaluated waveform samples</p>
      </section>
      <section className="cnn-panel" aria-label="CNN software runtime"><h2>Measured software runtime</h2>
        <div className="metric-strip"><div><span>Vectorised NumPy</span><strong>{(1000 * result.numpy_seconds).toFixed(3)} ms</strong></div>
          <div><span>Prabha {result.execution_mode === 'symbol' ? 'constant-symbol' : 'sampled waveform'}</span><strong>{(1000 * result.prabha_seconds).toFixed(3)} ms</strong></div></div>
        <p className="hint">{result.timing_scope} These software runtimes do not measure physical photonic hardware.</p>
      </section>
    </>}
    {benchmark && <section className="cnn-panel" aria-label="Execution benchmark">
      <h2>Repeated execution benchmark</h2>
      <p>{benchmark.count} images, {benchmark.blocks} measured blocks, {benchmark.warmups_excluded} excluded warmup blocks.</p>
      <div className="metric-strip">
        <div><span>NumPy median</span><strong>{(1000 * benchmark.median_seconds.numpy).toFixed(3)} ms</strong></div>
        <div><span>Sampled median</span><strong>{(1000 * benchmark.median_seconds.waveform).toFixed(3)} ms</strong></div>
        <div><span>Constant-symbol median</span><strong>{(1000 * benchmark.median_seconds.symbol).toFixed(3)} ms</strong></div>
      </div>
      <p>Sampled / constant-symbol: {benchmark.waveform_over_symbol.toFixed(2)}×. Maximum logit difference: {sci(benchmark.maximum_symbol_waveform_logit_difference)}.</p>
      <p className="hint">{benchmark.timing_scope} {benchmark.claim_scope}</p>
      <button className="text-button" disabled={busy} onClick={() => runTask(() => save('prabha-execution-benchmark.json', JSON.stringify(benchmark, null, 2)))}>Export benchmark JSON ↓</button>
    </section>}
    <p className="scope-note">8 × 8 digits · 1,149 training / 288 validation / 360 held-out images. Bias, ReLU, pooling and scaling include digital/software operations. Noise is disabled in this network. Native scalar/RIN validation has its own documented configuration.</p>
  </div>;
}
