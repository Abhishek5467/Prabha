import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';

async function open(page,path='/designer') {
  await page.goto(path);
  await expect(page.locator('#exampleNote')).toContainText('Read adc.voltage');
  await expect(page.locator('.node')).toHaveCount(8);
}
async function run(page) {
  await page.locator('#runBtn').click();
  await expect(page.locator('#results')).toContainText('components-1');
}
async function exported(page) {
  const pending=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export reproducible run (.json)',exact:true}).click();
  return JSON.parse(await readFile(await(await pending).path(),'utf8'));
}
async function chooseNode(page,title) {
  await page.locator('.node').filter({has:page.locator('.node-title',{hasText:title})}).locator('.hd').click();
}

test('Designer current models, quantization change, stale results and replayable export',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await open(page);await expect(page.locator('#palette .pblock')).toHaveCount(19);
  const input=page.locator('.node').filter({has:page.locator('.node-title',{hasText:'Normalized input x'})});
  const weight=page.locator('.node').filter({has:page.locator('.node-title',{hasText:'Signed weight w'})});
  await expect(input).toContainText('x = [0.9, 0.3, 0.7, 0.5]');
  await expect(weight).toContainText('w = [0.8, -0.6, 0.4, -0.9]');
  await weight.locator('.hd').click();await expect(page.locator('.source-role')).toContainText('dimensionless');
  await run(page);await expect(page.locator('#scopeView')).toBeDisabled();const first=await exported(page);
  expect(first.result.probes.adc.voltage.last).toBe(0.6388278388278388);
  expect(first.result.probes.adc.code.last).toBe(2616);
  expect(first.request.action).toBe('graph');expect(first.request.noise).toBe(false);expect(first.request.duration).toBe(4e-9);
  await chooseNode(page,'Photonic MAC (component models)');
  await expect(page.locator('#insBody')).toContainText('nonlinear MZM');
  await page.locator('#param-dac_bits').fill('3');await page.locator('#param-dac_bits').press('Tab');
  await expect(page.locator('#results')).toBeEmpty();await run(page);
  const next=await exported(page);expect(next.result.probes.adc.voltage.last).not.toBe(first.result.probes.adc.voltage.last);
  await page.locator('#runSeed').fill('7');await page.locator('#runSeed').press('Tab');
  await expect(page.locator('#results')).toBeEmpty();
  expect(errors).toEqual([]);
});

test('Project settings round trip, expanded graph and model errors',async({page})=>{
  await open(page);
  await page.locator('#exampleSel').selectOption('expanded');
  await expect(page.locator('#exampleNote')).toContainText('Same chain');await run(page);
  expect((await exported(page)).result.probes.adc.voltage.last).toBe(0.6388278388278388);
  page.once('dialog',d=>d.accept('expanded-models'));
  const pending=page.waitForEvent('download');
  await page.keyboard.press('Control+s');
  const file=JSON.parse(await readFile(await(await pending).path(),'utf8'));
  expect(file.format).toBe('prabha-designer/1');expect(file.settings.duration_ns).toBe(4);
  await page.locator('#exampleSel').selectOption('receiver');
  await expect(page.locator('#exampleNote')).toContainText('Inspect laser');
  await page.locator('#imp').setInputFiles({name:'saved.prabha.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(file))});
  await expect(page.locator('#durationNs')).toHaveValue('4');await expect(page.locator('#noise')).not.toBeChecked();
  await chooseNode(page,'ADC');
  await page.locator('#param-v_max').fill('0.1');await page.locator('#param-v_max').press('Tab');
  await page.locator('#runBtn').click();await expect(page.locator('#violBox')).toContainText('above ADC range');
  await expect(page.locator('#results')).toBeEmpty();
  await page.locator('#param-clip').selectOption('true');await run(page);
  expect((await exported(page)).result.probes.adc.code.last).toBe(4095);
});

test('Receiver noise controls, phase scope and legacy compatibility',async({page})=>{
  await open(page);await page.locator('#exampleSel').selectOption('receiver');
  await expect(page.locator('#exampleNote')).toContainText('Inspect laser');
  await expect(page.locator('#noise')).toBeChecked();await run(page);
  const result=await exported(page);expect(result.result.probes.laser.out.phase_rad.length).toBe(512);
  await page.locator('#scopeSel').selectOption({label:'laser.out (W)'});await page.locator('#scopeView').selectOption('phase');
  await expect(page.locator('#scope')).toContainText('rad');
  await expect(page.locator('#scopeView')).toBeEnabled();
  await page.locator('#scopeSel').selectOption({label:'tia.out (V)'});
  await expect(page.locator('#scopeView')).toBeDisabled();await expect(page.locator('#scopeView')).toHaveValue('power');
  await chooseNode(page,'Transimpedance amplifier');await expect(page.locator('#param-noise_A_sqrtHz')).toHaveValue('1e-12');
  await page.locator('#exampleSel').selectOption('legacy');await expect(page.locator('#exampleNote')).toContainText('Historical PEMAN');
  await run(page);await expect(page.locator('#results h3')).toHaveText('Results · legacy-peman');expect((await exported(page)).result.model_profiles).toEqual(['legacy-peman']);
});
