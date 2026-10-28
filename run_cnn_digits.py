"""Train a labelled CNN, transfer fixed weights, and evaluate the full test set.

No PyTorch/GPU required. The packaged data snapshot allows offline repeats.
"""
from pathlib import Path
from dataclasses import asdict
import argparse,csv,hashlib,json,os,platform,sys,time
import numpy as np

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'core-py'))
from prabha.systems.cnn_training import train,forward
from prabha.systems.cnn import conv2d,relu,max_pool2d,linear
from prabha.systems.mac import MACConfig,PhysicalMAC,DigitalMAC

def operator_forward(x,p,backend):
    features=max_pool2d(relu(conv2d(x,p['conv_weight'],p['conv_bias'],backend=backend)))
    return linear(features.reshape(len(x),-1),p['dense_weight'],p['dense_bias'],backend=backend)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_data(path):
    if not path.exists():
        from sklearn.datasets import load_digits
        from sklearn.model_selection import train_test_split
        d=load_digits()
        indices=np.arange(len(d.target))
        rest,test=train_test_split(indices,test_size=.2,stratify=d.target,random_state=20261015)
        training,validation=train_test_split(rest,test_size=.2,stratify=d.target[rest],random_state=20261016)
        path.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(path,images=d.images.astype(np.uint8),labels=d.target.astype(np.int64),
                            train_indices=training,validation_indices=validation,test_indices=test)
    with np.load(path,allow_pickle=False) as a:
        arrays={k:a[k].copy() for k in a.files}
    ids=[set(arrays[k].tolist()) for k in ['train_indices','validation_indices','test_indices']]
    assert not any(ids[i]&ids[j] for i in range(3) for j in range(i))
    assert set.union(*ids)==set(range(len(arrays['labels'])))
    return arrays

def write_csv(path,rows):
    with path.open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-model',action='store_true',help='Evaluate the saved selected checkpoint without retraining.')
    parser.add_argument('--epochs',type=int,default=160)
    parser.add_argument('--execution',choices=['auto','symbol','waveform'],default='waveform')
    parser.add_argument('--batch-size',type=int,default=30,help='Inference timing batch size; final batch may be smaller.')
    args=parser.parse_args()
    out=ROOT/'results/cnn_digits';out.mkdir(parents=True,exist_ok=True)
    data_path=ROOT/'validation/datasets/digits_8x8_split.npz'
    data=load_data(data_path)
    x=data['images'][:,None].astype(np.float64)/16
    y=data['labels']
    train_ids,val_ids,test_ids=(data[k] for k in ['train_indices','validation_indices','test_indices'])
    model_path=out/'trained_cnn.npz';training_info=out/'training_metadata.json'
    if not args.reuse_model:
        start=time.perf_counter()
        p,history,best_epoch=train(x[train_ids],y[train_ids],x[val_ids],y[val_ids],epochs=args.epochs)
        training_seconds=time.perf_counter()-start
        np.savez_compressed(model_path,**p)
        write_csv(out/'training_history.csv',history)
        info={'epochs_run':args.epochs,'selected_epoch':best_epoch,'selection_rule':'Minimum validation cross-entropy; test labels not used for selection.',
              'training_seconds':training_seconds,'seed':20261015,'batch_size':64,'learning_rate':.005,
              'optimiser':'Adam, beta1=.9, beta2=.999, epsilon=1e-8','l2':1e-4,'filters':4,
              'dataset_sha256':sha(data_path),'model_sha256':sha(model_path)}
        training_info.write_text(json.dumps(info,indent=2)+'\n')
    info=json.loads(training_info.read_text())
    if info['dataset_sha256']!=sha(data_path) or info['model_sha256']!=sha(model_path):
        raise ValueError('Dataset or frozen model differs from the saved training record.')
    with np.load(model_path,allow_pickle=False) as checkpoint:p={k:checkpoint[k].copy() for k in checkpoint.files}
    xt,yt=x[test_ids],y[test_ids]
    config=MACConfig(dac_rounding='nearest_lower',mzm_extinction_ratio_db=100.,weight_extinction_ratio_db=100.)
    # Warm up each implementation before measured inference. Loading/training is excluded.
    forward(xt[:2],p);operator_forward(xt[:2],p,DigitalMAC());operator_forward(xt[:2],p,PhysicalMAC(config, execution=args.execution))
    conventional_times=[]
    for _ in range(7):
        start=time.perf_counter();reference=forward(xt,p);conventional_times.append(time.perf_counter()-start)
    start=time.perf_counter();operator_reference=operator_forward(xt,p,DigitalMAC());operator_seconds=time.perf_counter()-start
    np.testing.assert_allclose(operator_reference,reference,rtol=1e-11,atol=1e-11)
    backend=PhysicalMAC(config, execution=args.execution);physical=[];timings=[]
    for start_index in range(0,len(xt),args.batch_size):
        batch=xt[start_index:start_index+args.batch_size]
        start=time.perf_counter();physical.append(operator_forward(batch,p,backend));elapsed=time.perf_counter()-start
        timings.append({'first_test_position':start_index,'images':len(batch),'seconds':elapsed,'milliseconds_per_image':1000*elapsed/len(batch)})
        print(f'Prabha test images {min(start_index+len(batch),len(xt))}/{len(xt)}; batch {elapsed:.3f}s',flush=True)
    actual=np.concatenate(physical);error=actual-reference
    ref_pred=reference.argmax(1);physical_pred=actual.argmax(1)
    physical_seconds=sum(row['seconds'] for row in timings)
    confusion=np.zeros((10,10),dtype=int)
    for label,prediction in zip(yt,physical_pred,strict=True):confusion[label,prediction]+=1
    np.savez_compressed(out/'test_logits.npz',dataset_indices=test_ids,labels=yt,reference_logits=reference,prabha_logits=actual)
    predictions=[]
    for i in range(len(yt)):
        sorted_logits=np.sort(reference[i])
        predictions.append({'dataset_index':int(test_ids[i]),'label':int(yt[i]),'reference_prediction':int(ref_pred[i]),
                            'prabha_prediction':int(physical_pred[i]),'reference_margin':float(sorted_logits[-1]-sorted_logits[-2]),
                            'maximum_logit_error':float(np.max(abs(error[i])))})
    write_csv(out/'test_predictions.csv',predictions);write_csv(out/'inference_batch_times.csv',timings)
    np.savetxt(out/'confusion_matrix.csv',confusion,delimiter=',',fmt='%d',header='columns: predicted digits 0..9; rows: true digits 0..9')
    source_files=['run_cnn_digits.py','core-py/prabha/systems/cnn_training.py','core-py/prabha/systems/cnn.py',
                  'core-py/prabha/systems/mac.py','core-py/prabha/blocks/dac.py','core-py/prabha/blocks/mzm.py',
                  'core-py/prabha/blocks/cw_laser.py','core-py/prabha/blocks/photodetector.py','core-py/prabha/blocks/capacitor.py']
    result={'dataset':'scikit-learn bundled digits, UCI optical recognition subset; 8x8 pixels, ten classes',
            'dataset_reference':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html',
            'preprocessing':'uint8 pixel intensities divided by 16; no fitted preprocessing; NCHW float64',
            'split':{'train':len(train_ids),'validation':len(val_ids),'test':len(test_ids),'stratified':True,
                     'split_seeds':[20261015,20261016],'writer_disjoint':False},
            'architecture':'8x8 -> Conv(1,4,3 valid) -> ReLU -> MaxPool(2) -> flatten 36 -> Linear(36,10)',
            'parameter_count':sum(a.size for a in p.values()),'training':info,'physical_config':asdict(config),
            'reference_correct':int(np.sum(ref_pred==yt)),'prabha_correct':int(np.sum(physical_pred==yt)),
            'test_images':len(yt),'reference_accuracy':float(np.mean(ref_pred==yt)),
            'prabha_accuracy':float(np.mean(physical_pred==yt)),
            'prediction_disagreements':int(np.sum(ref_pred!=physical_pred)),
            'logit_rms_error':float(np.sqrt(np.mean(error**2))),'logit_max_abs_error':float(np.max(abs(error))),
            'reference_operator_max_abs_error':float(np.max(abs(operator_reference-reference))),
            'physical_mac_calls':backend.calls,'device_passes':backend.device_passes,'waveform_samples':backend.waveform_samples,
            'timing':{'vectorised_numpy_seconds_all_test_median_7':float(np.median(conventional_times)),
                      'vectorised_numpy_seconds_all_test_runs':conventional_times,
                      'shared_operators_digital_mac_seconds_all_test_single_run':operator_seconds,
                      'prabha_seconds_all_test_single_pass':physical_seconds,
                      'prabha_images_per_second':len(yt)/physical_seconds,
                      'prabha_milliseconds_per_image_amortised':1000*physical_seconds/len(yt),
                      'prabha_inference_batches':len(timings),'batch_size':args.batch_size,
                      'scope':'Warm CPU software inference, resident inputs/weights; single full Prabha pass in batches. Loading/training excluded. No hardware latency claim.'},
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),
                           'processor':platform.processor(),'openblas_threads':os.environ.get('OPENBLAS_NUM_THREADS')},
            'source_sha256':{name:sha(ROOT/name) for name in source_files},
            'native_full_cnn_run':False,'noise_enabled':False,'weight_training':'Digital NumPy CNN; fixed transferred weights; no physical/noise-aware retraining.',
            'limitations':['Small random image-stratified holdout, not a writer-disjoint or official MNIST test.',
                           'Automatic per-MAC input/weight normalisation, digital biases/ReLU/pooling and tiled digital sums.',
                           'Output ADC disabled; no noise, native CNN switching/reset validation or hardware measurements.',
                           'Native stationary RIN endpoint remains inconclusive; earlier 68/69 decision unchanged.',
                           'One physical timing pass, machine-specific; conventional NumPy reference is not PyTorch/GPU or hardware.']}
    (out/'cnn_digits_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['reference_accuracy','prabha_accuracy','prediction_disagreements','logit_rms_error','logit_max_abs_error']}),flush=True)
    print('Saved complete trained CNN result:',out,flush=True)

if __name__=='__main__':main()
