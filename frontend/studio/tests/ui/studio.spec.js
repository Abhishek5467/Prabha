import {test, expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';

async function downloadedJson(page, name) {
  const download = page.waitForEvent('download');
  await page.getByRole('button', {name, exact: true}).click();
  return JSON.parse(await readFile(await (await download).path(), 'utf8'));
}

test('ANN inference, complete exports, import, stale results and reference batch', async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/#ann');
  await page.getByRole('button', {name: 'Run inference'}).click();
  await expect(page.getByRole('button', {name: 'Export inference JSON ↓', exact: true})).toBeVisible();
  const record = await downloadedJson(page, 'Export inference JSON ↓');
  expect(record.schema).toBe('prabha.run.v1');
  expect(record.engine).toBe('Python API');
  expect(record.engine_version).toBe('0.1.0-preview.3');
  expect(record.request.inputs).toEqual([0.9, 0.3, 0.7, 0.5]);
  expect(record.request.network.w1).toHaveLength(3);
  expect(record.result.physical_output).toHaveLength(2);
  await page.getByLabel('Input 1 value', {exact: true}).fill('');
  await expect(page.getByRole('button', {name: 'Export inference JSON ↓', exact: true})).toHaveCount(0);
  await page.getByRole('button', {name: 'Run inference'}).click();
  await expect(page.getByRole('alert')).toContainText('Input 1 is required');
  await page.getByLabel('Import ANN JSON', {exact: true}).setInputFiles({
    name: 'previous-run.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(record))
  });
  await expect(page.getByLabel('Input 1 value', {exact: true})).toHaveValue('0.9');
  await page.getByRole('button', {name: 'Validate 100 inputs', exact: true}).click();
  await expect(page.getByRole('region', {name: 'Batch validation'})).toContainText('7.8644e-5');
  const batch = await downloadedJson(page, 'Export batch JSON ↓');
  expect(Math.abs(batch.result.rms_error - 7.864411795585e-5)).toBeLessThan(1e-12);
  expect(batch.result.winner_mismatches).toBe(0);
  expect(batch.request.seed).toBe(12345);
  const download = page.waitForEvent('download');
  await page.getByRole('button', {name: 'Export CSV ↓', exact: true}).click();
  const csv = await readFile(await (await download).path(), 'utf8');
  expect(csv.trim().split('\n')).toHaveLength(101);
  await page.getByRole('combobox', {name: 'DAC', exact: true}).selectOption('4');
  await expect(page.getByRole('region', {name: 'Batch validation'})).toHaveCount(0);
  await expect(page.getByText('Exploratory configuration', {exact: true})).toBeVisible();
  expect(errors).toEqual([]);
});

test('component controls clear stale curves; exports include seeded laser settings', async ({page}) => {
  await page.goto('/#components');
  await page.getByRole('button', {name: 'Run experiment'}).click();
  const mzm = await downloadedJson(page, 'Export experiment JSON ↓');
  expect(mzm.request.kind).toBe('mzm');
  expect(mzm.result.x).toHaveLength(401);
  await page.getByLabel('Half-wave voltage, Vπ (V)', {exact: true}).fill('2');
  await expect(page.getByRole('button', {name: 'Export experiment JSON ↓', exact: true})).toHaveCount(0);
  await page.getByRole('combobox', {name: 'Component', exact: true}).selectOption('laser');
  await page.getByRole('button', {name: 'Run experiment'}).click();
  const laser = await downloadedJson(page, 'Export experiment JSON ↓');
  expect(laser.request.seed).toBe(1);
  expect(laser.request.linewidth_hz).toBe(1e6);
  expect(laser.result.x).toHaveLength(1600);
});

test('native bridge routes exports and external links without leaving Studio', async ({page}) => {
  // JS contract check only; this does not claim to test a native installer/dialog.
  await page.addInitScript(() => {
    window.nativeCalls = [];
    window.__TAURI__ = {core: {invoke: async (command, payload) => {
      if (command === 'simulate') return (await fetch('/api/execute', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload.payload)
      })).json();
      window.nativeCalls.push({command, payload});
      return true;
    }}};
  });
  await page.goto('/#ann');
  await page.getByRole('button', {name: 'Run inference'}).click();
  await page.getByRole('button', {name: 'Export inference JSON ↓', exact: true}).click();
  await expect(page.getByText('Export ready: prabha-infer.json')).toBeVisible();
  await page.getByRole('link', {name: 'Community forum ↗', exact: true}).click();
  const calls = await page.evaluate(() => window.nativeCalls);
  const file = calls.find(item => item.command === 'save_export');
  expect(JSON.parse(Buffer.from(file.payload.bytes).toString()).engine).toBe('Desktop Python');
  expect(calls.find(item => item.command === 'open_external').payload.url).toBe('https://prabhacommunity5701.flarum.cloud/');
  expect(page.url()).toContain('/#ann');
});

test('Pages subpath, mobile layout, docs and community links', async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('http://127.0.0.1:8081/Prabha/');
  await expect(page.getByRole('heading', {name: 'Light, models and reproducible experiments.'})).toBeVisible();
  await expect(page.getByRole('link', {name: 'Discord chat ↗', exact: true})).toHaveAttribute('href', 'https://discord.gg/RUdRMHBFp');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.goto('http://127.0.0.1:8081/Prabha/#evidence');
  await expect(page.getByRole('button', {name: /^Enlarge /})).toHaveCount(25);
  await page.getByRole('button', {name: /^Enlarge /}).first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await page.getByRole('link', {name: 'Documentation ↗', exact: true}).click();
  await expect(page.getByRole('link', {name: '← Back to Prabha Studio', exact: true})).toHaveAttribute('href', 'http://127.0.0.1:8081/Prabha/');
  await page.goto('http://127.0.0.1:8081/Prabha/docs/community/');
  await expect(page.locator('#community-join-link')).toHaveAttribute('href', 'https://prabhacommunity5701.flarum.cloud/');
  await expect(page.locator('#community-chat-link')).toHaveAttribute('href', 'https://discord.gg/RUdRMHBFp');
  expect(errors).toEqual([]);
});
