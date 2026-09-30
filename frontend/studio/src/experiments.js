export const DEFAULT_INPUTS = [0.9, 0.3, 0.7, 0.5];
export const DEFAULT_NETWORK = {
  w1: [[0.8, -0.6, 0.4, -0.9], [-0.3, 0.7, 0.5, 0.2], [0.6, 0.1, -0.8, 0.7]],
  b1: [0.2, -0.1, 0.05], w2: [[0.7, -0.5, 0.6], [-0.4, 0.9, -0.7]], b2: [0.1, -0.05]
};
export const PRECISIONS = Array.from({length: 14}, (_, i) => i + 3);
export function numberInRange(value, name, low, high) {
  if (value === '' || value === null || typeof value === 'boolean' ||
      !['number', 'string'].includes(typeof value) ||
      (typeof value === 'string' && !value.trim())) throw new Error(name + ' is required.');
  const number = Number(value);
  if (!Number.isFinite(number) || number < low || number > high)
    throw new Error(name + ' must be between ' + low + ' and ' + high + '.');
  return number;
}
function vector(value, length, name, low, high) {
  if (!Array.isArray(value) || value.length !== length) throw new Error(name + ' must contain ' + length + ' numbers.');
  return value.map((item, i) => {
    if (typeof item !== 'number') throw new Error(name + ' must contain numbers.');
    return numberInRange(item, name + '[' + i + ']', low, high);
  });
}
export function validateNetwork(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Network must be a JSON object.');
  const matrix = (key, rows, cols) => {
    if (!Array.isArray(value[key]) || value[key].length !== rows) throw new Error(key + ' must have ' + rows + ' rows.');
    return value[key].map((row, i) => vector(row, cols, key + '[' + i + ']', -1, 1));
  };
  return {w1: matrix('w1', 3, 4), b1: vector(value.b1, 3, 'b1', -10, 10),
    w2: matrix('w2', 2, 3), b2: vector(value.b2, 2, 'b2', -10, 10)};
}
export function parseNetwork(text) {
  let value;
  try { value = JSON.parse(text); } catch { throw new Error('Network JSON is invalid. Check commas and brackets, or restore the reference network.'); }
  return validateNetwork(value);
}
export function validateInputs(values) {
  if (!Array.isArray(values) || values.length !== 4) throw new Error('Exactly four inputs are required.');
  return values.map((value, i) => numberInRange(value, 'Input ' + (i + 1), 0, 1));
}
export function isReference(request) {
  return request.dac_bits === 12 && request.adc_bits === 12 &&
    JSON.stringify(request.network) === JSON.stringify(DEFAULT_NETWORK);
}
export function importAnn(text) {
  let file;
  try { file = JSON.parse(text); } catch { throw new Error('Choose a valid Prabha JSON file.'); }
  let settings;
  if (file?.schema === 'prabha.ann-settings.v1') settings = file.settings;
  else if (file?.schema === 'prabha.run.v1' && ['infer', 'batch'].includes(file.request?.action)) {
    const request = file.request;
    if (request.action === 'batch' && (request.count !== 100 || request.seed !== 12345 || request.inputs))
      throw new Error('Studio imports batch runs with 100 samples and seed 12345. Use the API for other batches.');
    settings = {...request, inputs: request.action === 'batch' ? DEFAULT_INPUTS : request.inputs};
  } else throw new Error('Import ANN settings or an ANN run exported by this version of Studio.');
  if (!settings || !PRECISIONS.includes(settings.dac_bits) || !PRECISIONS.includes(settings.adc_bits))
    throw new Error('DAC and ADC precision must be integers from 3 to 16.');
  return {inputs: vector(settings.inputs, 4, 'inputs', 0, 1),
    dac_bits: settings.dac_bits, adc_bits: settings.adc_bits, network: validateNetwork(settings.network)};
}
export function batchCsv(record) {
  const rows = record.result.rows.map(row =>
    [row.sample, ...row.inputs, ...row.ideal, ...row.physical, ...row.error,
      record.request.seed, record.request.dac_bits, record.request.adc_bits,
      record.engine_version, record.engine].join(','));
  return 'sample,x1,x2,x3,x4,ideal_y1,ideal_y2,physical_y1,physical_y2,error_y1,error_y2,seed,dac_bits,adc_bits,engine_version,engine\n' + rows.join('\n') + '\n';
}
