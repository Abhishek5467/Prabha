// CNN settings are data only. Imported results are never trusted as computation.
const SHAPES = {conv_weight:[4,1,3,3],conv_bias:[4],dense_weight:[10,36],dense_bias:[10]};
function keys(value, expected, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).sort().join('|') !== [...expected].sort().join('|'))
    throw new Error(name + ' has missing or unsupported fields.');
}
function number(value, name, low, high, integer=false) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < low || value > high ||
      (integer && !Number.isInteger(value))) throw new Error(name + ' must be ' + (integer?'an integer':'a number') + ' between ' + low + ' and ' + high + '.');
  return value;
}
function array(value, shape, name, low, high) {
  if (!shape.length) return number(value,name,low,high);
  if (!Array.isArray(value) || value.length !== shape[0]) throw new Error(name + ' has the wrong shape; expected [' + shape + '].');
  return value.map((item,i)=>array(item,shape.slice(1),name+'['+i+']',low,high));
}
export function validateSettings(value) {
  keys(value,['input','model','converters'],'Settings');
  keys(value.input,['mode','count','start','pixels','label'],'Input');
  keys(value.model,Object.keys(SHAPES),'Model');
  keys(value.converters,['dac_bits','adc_bits','adc_full_scale','dac_rounding'],'Converters');
  const source=value.input,c=value.converters;
  if (!['heldout','custom'].includes(source.mode)) throw new Error('Choose heldout or custom input.');
  const count=number(source.count,'count',1,360,true),start=number(source.start,'start',0,359,true);
  if (start+count>360) throw new Error('The held-out range must end at or before image 360.');
  const pixels=array(source.pixels,[8,8],'pixels',0,16);
  const label=source.label===null?null:number(source.label,'label',0,9,true);
  const model=Object.fromEntries(Object.entries(SHAPES).map(([key,shape])=>[key,array(value.model[key],shape,key,-100,100)]));
  for (const key of ['dac_bits','adc_bits']) if(c[key]!==null)number(c[key],key,1,24,true);
  number(c.adc_full_scale,'ADC full scale',.001,1e6);
  if (!['nearest_lower','nearest_even'].includes(c.dac_rounding)) throw new Error('Unsupported DAC rounding convention.');
  return {input:{mode:source.mode,count,start,pixels,label},model,converters:{...c}};
}
export function parseSettingsFile(text) {
  let value;
  try {value=JSON.parse(text);} catch {throw new Error('Choose valid CNN settings JSON.');}
  if (!['prabha.cnn-settings.v1','prabha.cnn-run.v2'].includes(value?.schema))
    throw new Error('Import CNN settings or an editable-CNN run exported by this version.');
  return validateSettings(value.settings);
}
export function settingsDocument(settings) {
  return {schema:'prabha.cnn-settings.v1',settings:validateSettings(settings)};
}
export function resultsCsv(result) {
  const rows=result.rows.map((r,i)=>[i+1,r.test_position===null?'custom':r.test_position+1,
    r.label??'',r.numpy_prediction,r.prabha_prediction,r.correct===null?'unlabelled':r.correct,
    r.maximum_logit_error,result.configuration.dac_bits??'off',result.configuration.adc_bits??'off',
    result.numpy_seconds,result.prabha_seconds,result.effective_weights_sha256].join(','));
  return 'row,test_image,true_digit,numpy_prediction,prabha_prediction,correct,max_logit_error,dac_bits,adc_bits,numpy_seconds,prabha_seconds,effective_weights_sha256\n'+rows.join('\n')+'\n';
}
