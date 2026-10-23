"""Recreate report figures from recorded numerical CNN workspace experiments."""
from pathlib import Path
import argparse,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser();parser.add_argument('--data-dir',type=Path,required=True);parser.add_argument('--out-dir',type=Path,required=True);args=parser.parse_args()
args.out_dir.mkdir(parents=True,exist_ok=True)
data=json.loads((args.data_dir/'workspace_validation.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
p=data['profiles'];base=p[0]
fig,axes=plt.subplots(2,1,figsize=(6.5,6.0),layout='constrained')
labels=['12-bit DAC\nADC off','4-bit DAC\nADC off','4-bit DAC\n8-bit ADC']
bars=axes[0].bar(labels,[100*r['prabha_accuracy'] for r in p],color=['#245d68','#a5814c','#b45442'],width=.58)
axes[0].axhline(100*base['numpy_accuracy'],ls='--',color='#3d454a',lw=1,label='NumPy: 98.33%')
for bar,r in zip(bars,p):axes[0].text(bar.get_x()+bar.get_width()/2,bar.get_height()-6,f"{r['prabha_correct']}/360",ha='center',va='top',fontsize=9,color='white',weight='semibold')
axes[0].set(ylim=(0,108),ylabel='Classification accuracy (%)',title='(a) Converter controls change the physical-model result')
axes[0].legend(loc='lower right',frameon=False,fontsize=9)
times=[base['numpy_seconds'],base['shared_digital_seconds'],base['prabha_seconds']]
bars=axes[1].bar(['Vectorised\nNumPy','Shared operators\nDigitalMAC','Prabha\nwaveforms'],times,color=['#6c8e89','#a4afaa','#b57b42'],width=.58)
axes[1].set_yscale('log');axes[1].set(ylabel='Warm inference time (s, log scale)',title='(b) Reference profile: 360 images, same trained weights',ylim=(min(times)*.25,max(times)*4))
for bar,t in zip(bars,times):axes[1].text(bar.get_x()+bar.get_width()/2,t*1.18,f'{t:.4g} s',ha='center',fontsize=9)
for ax in axes:ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.savefig(args.out_dir/'CNN_Workspace_Controls.pdf');fig.savefig(args.out_dir/'CNN_Workspace_Controls.png',dpi=180);plt.close(fig)
layer=json.loads((args.data_dir/'selected_layer.json').read_text())
conv=next(v for v in layer['inspection']['layers'] if v['name']=='convolution')
a,b=np.asarray(conv['numpy'])[2],np.asarray(conv['prabha'])[2];d=b-a
fig,axes=plt.subplots(1,3,figsize=(7.0,2.65),layout='constrained')
low,high=min(a.min(),b.min()),max(a.max(),b.max())
for ax,z,title in zip(axes[:2],[a,b],['NumPy','Prabha']):
    im=ax.imshow(z,cmap='viridis',vmin=low,vmax=high);ax.set_title(title);ax.set_xticks([0,2,4]);ax.set_yticks([0,2,4])
fig.colorbar(im,ax=axes[:2],shrink=.72,label='Convolution value')
extent=float(np.max(abs(d)));im=axes[2].imshow(d,cmap='RdBu_r',vmin=-extent,vmax=extent);axes[2].set_title('Prabha - NumPy');axes[2].set_xticks([0,2,4]);axes[2].set_yticks([0,2,4]);fig.colorbar(im,ax=axes[2],shrink=.72,format='%.1e')
fig.suptitle('Held-out image 2, convolution channel 2 (zero-based)',fontsize=10)
fig.savefig(args.out_dir/'CNN_Workspace_Layer.pdf');fig.savefig(args.out_dir/'CNN_Workspace_Layer.png',dpi=180);plt.close(fig)
