"""Rebuild the trained-CNN scientific figure from saved measured records."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    out=Path(__file__).resolve().parent/'results/cnn_digits'
    r=json.loads((out/'cnn_digits_results.json').read_text())
    history=list(csv.DictReader((out/'training_history.csv').open()))
    epochs=[int(x['epoch']) for x in history]
    with np.load(out/'test_logits.npz',allow_pickle=False) as a:
        reference=a['reference_logits'];actual=a['prabha_logits']
    confusion=np.loadtxt(out/'confusion_matrix.csv',delimiter=',',comments='#')
    plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','axes.spines.top':False,
                         'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(7.2,6.1),layout='constrained')
    ax=axes[0,0]
    for key,label in [('train_loss','Training'),('validation_loss','Validation')]:
        ax.plot(epochs,[float(x[key]) for x in history],label=label,lw=1.3)
    ax.axvline(r['training']['selected_epoch'],ls=':',color='black',lw=1,label='Selected epoch')
    ax.set(xlabel='Epoch',ylabel='Cross-entropy',yscale='log',title='(a) Digital CNN training')
    ax.legend(fontsize=7,frameon=False);ax.grid(alpha=.2)
    ax=axes[0,1]
    ax.imshow(confusion,cmap='Blues',vmin=0,vmax=confusion.max())
    for i in range(10):
        for j in range(10):
            if confusion[i,j]:ax.text(j,i,str(int(confusion[i,j])),ha='center',va='center',fontsize=6.5,color='white' if confusion[i,j]>confusion.max()/2 else 'black')
    ax.set(xticks=range(10),yticks=range(10),xlabel='Predicted digit',ylabel='True digit',
           title='(b) Prabha: 354/360 correct')
    ax=axes[1,0]
    ax.scatter(reference.reshape(-1),actual.reshape(-1),s=2,alpha=.35,color='#245a81',rasterized=True)
    limits=[float(min(reference.min(),actual.min())),float(max(reference.max(),actual.max()))]
    ax.plot(limits,limits,color='black',ls='--',lw=.8)
    ax.set(xlabel='Reference logit',ylabel='Prabha logit',title='(c) All 3,600 test logits')
    ax.grid(alpha=.2)
    ax=axes[1,1];t=r['timing']
    values=[t['vectorised_numpy_seconds_all_test_median_7'],t['shared_operators_digital_mac_seconds_all_test_single_run'],t['prabha_seconds_all_test_single_pass']]
    ax.bar(range(3),values,color=['#6b8ca6','#5d9b8a','#c17d43'],width=.65)
    ax.set(xticks=range(3),xticklabels=['Vectorised\nNumPy','Shared ops\nDigitalMAC','Prabha\nPhysicalMAC'],yscale='log',ylabel='Seconds for 360 images',title='(d) Warm CPU inference')
    for i,v in enumerate(values):ax.text(i,v*1.2,f'{v:.4g}',ha='center',va='bottom',fontsize=8)
    ax.set_ylim(min(values)/2,max(values)*5);ax.grid(axis='y',alpha=.2)
    fig.savefig(out/'Prabha_Trained_CNN.pdf',bbox_inches='tight')
    fig.savefig(out/'Prabha_Trained_CNN.png',dpi=210,bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':main()
