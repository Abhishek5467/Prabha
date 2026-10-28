import {test, expect} from '@playwright/test';
import {readFile, mkdir, writeFile} from 'node:fs/promises';

async function exported(page, name) {
  const download = page.waitForEvent('download');
  await page.getByRole('button', {name, exact: true}).click();
  return JSON.parse(await readFile(await (await download).path(), 'utf8'));
}
async function openCnn(page) {
  await page.goto('/#cnn');
  await expect(page.getByRole('button', {name: 'Run CNN inference'})).toBeEnabled();
  await expect(page.locator('iframe')).toHaveCount(0);
}

test('execution choice changes the actual backend, survives exports and has a separate benchmark', async ({page}) => {
  await openCnn(page);
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByRole('combobox', {name: 'Physical execution', exact: true}).selectOption('symbol');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  const fast = await exported(page, 'Export CNN run JSON ↓');
  expect(fast.result.execution_mode).toBe('symbol');
  expect(fast.result.materialized_waveform_samples).toBe(0);
  await page.getByRole('combobox', {name: 'Physical execution', exact: true}).selectOption('waveform');
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toHaveCount(0);
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  const sampled = await exported(page, 'Export CNN run JSON ↓');
  expect(sampled.result.execution_mode).toBe('waveform');
  expect(sampled.result.materialized_waveform_samples).toBeGreaterThan(0);
  sampled.result.rows[0].prabha_logits.forEach((v,i) => expect(Math.abs(v-fast.result.rows[0].prabha_logits[i])).toBeLessThan(1e-11));
  const saved = await exported(page, 'Export CNN settings ↓');
  expect(saved.execution).toBe('waveform');
  await page.getByRole('combobox', {name: 'Physical execution', exact: true}).selectOption('symbol');
  await page.getByLabel('Import CNN JSON', {exact: true}).setInputFiles({name:'mode.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))});
  await expect(page.getByRole('combobox', {name: 'Physical execution', exact: true})).toHaveValue('waveform');
  await page.getByRole('button', {name:'Benchmark both modes',exact:true}).click();
  await expect(page.getByRole('region',{name:'Execution benchmark',exact:true})).toContainText('3 measured blocks');
  const benchmark = await exported(page,'Export benchmark JSON ↓');
  expect(benchmark.rows).toHaveLength(9);
  expect(benchmark.symbol_waveform_prediction_disagreements).toBe(0);
});

test('native CNN validates all 360 images, exports exact results and inspects selected layers', async ({page}) => {
  test.setTimeout(90_000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await openCnn(page);
  await page.getByRole('button', {name: 'Validate 360 images', exact: true}).click();
  await expect(page.getByRole('region', {name: 'CNN results', exact: true})).toContainText('354/360', {timeout: 60_000});
  const record = await exported(page, 'Export CNN run JSON ↓');
  expect(record.schema).toBe('prabha.cnn-run.v3');
  expect(record.execution).toBe('auto');
  expect(record.result.execution_mode).toBe('symbol');
  expect(record.engine).toBe('Python API');
  expect(record.result.count).toBe(360);
  expect(record.result.numpy_correct).toBe(354);
  expect(record.result.prabha_correct).toBe(354);
  expect(record.result.prediction_disagreements).toBe(0);
  expect(record.settings).toEqual(record.result.settings);
  expect(record.result.mac_calls).toBe(55440);
  await page.getByRole('button', {name: 'Inspect prediction 15', exact: true}).click();
  await page.getByRole('combobox', {name: 'Stage', exact: true}).selectOption('convolution');
  await page.getByRole('combobox', {name: 'Feature channel', exact: true}).selectOption('3');
  await expect(page.getByRole('region', {name: 'CNN layer inspection', exact: true})).toContainText('Shape [4, 6, 6]');
  const layer = await exported(page, 'Export layer inspection ↓');
  expect(layer.selected_row).toBe(14);
  expect(layer.selected_stage).toBe('convolution');
  expect(layer.feature_channel).toBe(3);
  expect(layer.inspection.test_position).toBe(14);
  expect(layer.inspection.layers.at(-1).prabha).toEqual(record.result.rows[14].prabha_logits);
  const csvDownload = page.waitForEvent('download');
  await page.getByRole('button', {name: 'Export CNN CSV ↓', exact: true}).click();
  const csv = await readFile(await (await csvDownload).path(), 'utf8');
  expect(csv.trim().split('\n')).toHaveLength(361);
  await page.getByRole('link', {name: 'ANN inference', exact: true}).click();
  await page.getByRole('button', {name: 'Run inference'}).click();
  await expect(page.getByRole('button', {name: 'Export inference JSON ↓', exact: true})).toBeVisible();
  await page.getByRole('link', {name: 'Trained CNN', exact: true}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  await page.getByRole('combobox', {name: 'Input DAC', exact: true}).selectOption('4');
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toHaveCount(0);
  await expect(page.getByRole('region', {name: 'CNN layer inspection', exact: true})).toHaveCount(0);
  expect(errors).toEqual([]);
  await mkdir('../../results/cnn_studio', {recursive: true});
  await writeFile('../../results/cnn_studio/native_reference_run.json', JSON.stringify(record, null, 2) + '\n');
});

test('native CNN custom pixels, weights and converters change live computation; imports ignore predictions', async ({page}) => {
  await openCnn(page);
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByRole('spinbutton', {name: 'True digit (optional)', exact: true}).fill('');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  const original = await exported(page, 'Export CNN run JSON ↓');
  expect(original.result.numpy_accuracy).toBeNull();
  const value = structuredClone(original);
  value.settings.model.dense_bias[2] += .75;
  value.result.rows[0].prabha_prediction = 999;
  await page.getByLabel('Import CNN JSON', {exact: true}).setInputFiles({name: 'edited.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(value))});
  await expect(page.locator('.cnn-status')).toContainText('settings imported');
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toHaveCount(0);
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  const edited = await exported(page, 'Export CNN run JSON ↓');
  for (const path of ['numpy_logits', 'prabha_logits']) {
    const delta = edited.result.rows[0][path][2] - original.result.rows[0][path][2];
    expect(Math.abs(delta - .75)).toBeLessThan(1e-10);
  }
  const pixels = page.getByLabel('Editable pixel matrix', {exact: true});
  const before = JSON.parse(await pixels.inputValue());
  await page.getByRole('spinbutton', {name: 'Pixel brush', exact: true}).fill('7');
  await page.getByRole('button', {name: /^Pixel row 1 column 1,/}).click();
  const after = JSON.parse(await pixels.inputValue());
  expect(after[0][0]).toBe(7);
  expect(after.flat().slice(1)).toEqual(before.flat().slice(1));
  await page.getByRole('combobox', {name: 'Input DAC', exact: true}).selectOption('4');
  await page.getByRole('combobox', {name: 'MAC output ADC', exact: true}).selectOption('8');
  const settings = await exported(page, 'Export CNN settings ↓');
  expect(settings.settings.converters.dac_bits).toBe(4);
  expect(settings.settings.converters.adc_bits).toBe(8);
  expect(settings.settings.input.label).toBeNull();
  await page.getByRole('link', {name: 'ANN inference', exact: true}).click();
  await page.getByRole('link', {name: 'Trained CNN', exact: true}).click();
  expect(JSON.parse(await pixels.inputValue())[0][0]).toBe(7);
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  const quantized = await exported(page, 'Export CNN run JSON ↓');
  expect(quantized.result.configuration.adc_bits).toBe(8);
  expect(quantized.result.configuration.dac_bits).toBe(4);
  expect(quantized.result.rows[0].pixels[0]).toBe(7);
});

test('native CNN reports malformed edits and ADC range errors, then recovers', async ({page}) => {
  await openCnn(page);
  await page.getByRole('spinbutton', {name: 'Start index (0-based)', exact: true}).fill('');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('alert')).toContainText('required');
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByLabel('Editable pixel matrix', {exact: true}).fill('[[0]]');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('alert')).toContainText('wrong shape');
  await page.getByRole('button', {name: 'Reset CNN reference', exact: true}).click();
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByRole('combobox', {name: 'MAC output ADC', exact: true}).selectOption('8');
  await page.getByRole('spinbutton', {name: 'ADC ± range (V)', exact: true}).fill('0.001');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('alert')).toContainText('ADC range');
  await expect(page.locator('.cnn-status')).toContainText('failed');
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toHaveCount(0);
  await page.getByRole('spinbutton', {name: 'ADC ± range (V)', exact: true}).fill('64');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
});

test('native CNN uses the desktop simulation and Save bridge', async ({page}) => {
  await page.addInitScript(() => {
    window.nativeCalls = [];
    window.__TAURI__ = {core: {invoke: async (command, payload) => {
      window.nativeCalls.push({command, payload});
      if (command === 'simulate') return (await fetch('/api/execute', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload.payload)})).json();
      return true;
    }}};
  });
  await openCnn(page);
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true}).click();
  await expect(page.locator('.cnn-status')).toContainText('Export ready');
  const calls = await page.evaluate(() => window.nativeCalls);
  expect(calls.some(item => item.command === 'simulate' && item.payload.payload.action === 'cnn')).toBe(true);
  const save = calls.find(item => item.command === 'save_export');
  const record = JSON.parse(Buffer.from(save.payload.bytes).toString());
  expect(record.engine).toBe('Desktop Python');
  expect(record.result.count).toBe(1);
});

test('native CNN is responsive on mobile and loads at a repository subpath', async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await openCnn(page);
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.route('**/api/health', route => route.fulfill({json: {engine: 'native-python'}}));
  await page.route('**/api/execute', async route => {
    const response = await page.request.post('http://127.0.0.1:8000/api/execute', {data: route.request().postDataJSON()});
    await route.fulfill({response});
  });
  await page.goto('http://127.0.0.1:8081/Prabha/#cnn');
  await expect(page.getByRole('button', {name: 'Run CNN inference'})).toBeEnabled();
  await expect(page.locator('iframe')).toHaveCount(0);
  await page.getByRole('combobox', {name: 'Input source', exact: true}).selectOption('custom');
  await page.getByRole('button', {name: 'Run CNN inference'}).click();
  await expect(page.getByRole('button', {name: 'Export CNN run JSON ↓', exact: true})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
