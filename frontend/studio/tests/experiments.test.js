import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULT_INPUTS, DEFAULT_NETWORK, importAnn, validateInputs, parseNetwork, batchCsv} from '../src/experiments.js';

const settings = () => ({inputs: [...DEFAULT_INPUTS], network: structuredClone(DEFAULT_NETWORK), dac_bits: 12, adc_bits: 12});
test('ANN settings round-trip without trusting stored results', () => {
  const expected = settings();
  assert.deepEqual(importAnn(JSON.stringify({schema: 'prabha.ann-settings.v1', settings: expected})), expected);
  assert.deepEqual(importAnn(JSON.stringify({schema: 'prabha.run.v1', request: {action: 'infer', ...expected},
    result: {physical_output: ['untrusted']}})), expected);
});
test('invalid or incomplete values cannot silently become a valid experiment', () => {
  for (const bad of ['', ' ', null, false, -1, 2, NaN, Infinity])
    assert.throws(() => validateInputs([bad, 0, 0, 0]));
  assert.deepEqual(validateInputs(['0.9', 0.3, 0.7, 0.5]), DEFAULT_INPUTS);
  assert.throws(() => parseNetwork('{'));
  assert.throws(() => parseNetwork(JSON.stringify({...DEFAULT_NETWORK, w1: [[1, 2]]})));
  for (const change of [{adc_bits: 2}, {dac_bits: 3.5}, {inputs: ['0.9', 0.3, 0.7, 0.5]}, {network: null}])
    assert.throws(() => importAnn(JSON.stringify({schema: 'prabha.ann-settings.v1', settings: {...settings(), ...change}})));
  assert.throws(() => importAnn(JSON.stringify({physical_output: [0.1, 0.2]})));
});
test('standard batch imports preserve coefficients, while unsupported batches fail explicitly', () => {
  const request = {action: 'batch', count: 100, seed: 12345, network: DEFAULT_NETWORK, dac_bits: 4, adc_bits: 8};
  assert.deepEqual(importAnn(JSON.stringify({schema: 'prabha.run.v1', request})), {...settings(), dac_bits: 4, adc_bits: 8});
  for (const change of [{count: 20}, {seed: 7}, {inputs: [[0, 0, 0, 0]]}])
    assert.throws(() => importAnn(JSON.stringify({schema: 'prabha.run.v1', request: {...request, ...change}})));
});
test('batch CSV retains numerical rows and identifies precision, seed and engine', () => {
  const csv = batchCsv({engine: 'Python API', engine_version: '0.1.0-preview.2',
    request: {seed: 12345, dac_bits: 12, adc_bits: 12},
    result: {rows: [{sample: 0, inputs: [0, 0.1, 0.2, 0.3], ideal: [0.4, 0.5], physical: [0.41, 0.51], error: [0.01, 0.01]}]}});
  assert.equal(csv.trim().split('\n').length, 2);
  assert.match(csv, /12345,12,12,0.1.0-preview.2,Python API/);
  assert.equal(csv.trim().split('\n')[0].split(',').length, csv.trim().split('\n')[1].split(',').length);
});
