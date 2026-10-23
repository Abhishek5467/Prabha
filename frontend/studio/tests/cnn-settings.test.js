import test from 'node:test';
import assert from 'node:assert/strict';
import {validateSettings,parseSettingsFile,settingsDocument,resultsCsv} from '../public/cnn-settings.js';
const make=()=>({input:{mode:'custom',count:1,start:0,pixels:Array.from({length:8},()=>Array(8).fill(0)),label:null},
  model:{conv_weight:Array.from({length:4},()=>[Array.from({length:3},()=>Array(3).fill(0))]),conv_bias:Array(4).fill(0),dense_weight:Array.from({length:10},()=>Array(36).fill(0)),dense_bias:Array(10).fill(0)},
  converters:{dac_bits:12,adc_bits:null,adc_full_scale:64,dac_rounding:'nearest_lower'}});
test('CNN settings round-trip all edited tensors, inputs and converter choices',()=>{
  const s=make();s.model.conv_weight[2][0][1][1]=-.75;s.input.pixels[3][4]=12.5;s.converters.adc_bits=8;
  assert.deepEqual(parseSettingsFile(JSON.stringify(settingsDocument(s))),s);
});
test('CNN run import extracts settings and never imports stored predictions',()=>{
  const s=make();assert.deepEqual(parseSettingsFile(JSON.stringify({schema:'prabha.cnn-run.v2',settings:s,result:{accuracy:1,rows:['forged']}})),s);
  assert.throws(()=>parseSettingsFile(JSON.stringify({schema:'prabha.cnn-run.v1',result:{}})));
});
test('CNN validation rejects wrong shapes, strings, booleans and nonfinite values',()=>{
  for(const corrupt of [s=>s.input.pixels[0].pop(),s=>s.input.pixels[0][0]='3',s=>s.input.label=true,
    s=>s.model.dense_weight[0][0]=NaN,s=>s.model.conv_bias.pop(),s=>s.converters.adc_bits=false,
    s=>s.converters.dac_bits=25,s=>s.converters.adc_full_scale=0,s=>s.input.count=1.5,
    s=>{s.input.start=359;s.input.count=2;}]){const s=make();corrupt(s);assert.throws(()=>validateSettings(s));}
});
test('CNN CSV preserves unlabelled inputs and the exact converter profile',()=>{
  const text=resultsCsv({rows:[{test_position:null,label:null,numpy_prediction:3,prabha_prediction:3,correct:null,maximum_logit_error:.02}],configuration:{dac_bits:null,adc_bits:8},numpy_seconds:.01,prabha_seconds:1,effective_weights_sha256:'abc'});
  assert.match(text,/1,custom,,3,3,unlabelled,0.02,off,8,0.01,1,abc/);
});
