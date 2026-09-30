import React from 'react';
const fmt = (n, d = 6) => Number.isFinite(n) ? n.toFixed(d) : '—';
export function LineChart({x,y,xLabel,yLabel}){
 if(!x?.length)return null;
 const w=720,h=280,l=70,r=25,t=25,b=50;
 const xmin=Math.min(...x),xmax=Math.max(...x),rawMin=Math.min(...y),rawMax=Math.max(...y),pad=(rawMax-rawMin||1)*.08,ymin=rawMin-pad,ymax=rawMax+pad;
 const px=v=>l+(v-xmin)/(xmax-xmin||1)*(w-l-r),py=v=>h-b-(v-ymin)/(ymax-ymin||1)*(h-t-b);
 return <svg className="chart" viewBox={`0 0 ${w} ${h}`} role="img" aria-label={`${yLabel} versus ${xLabel}`}>
 {[0,.25,.5,.75,1].map(q=><g key={q}><line x1={l} y1={py(ymin+q*(ymax-ymin))} x2={w-r} y2={py(ymin+q*(ymax-ymin))} stroke="#e3e6e3"/><text x={l-10} y={py(ymin+q*(ymax-ymin))+4} textAnchor="end">{(ymin+q*(ymax-ymin)).toPrecision(3)}</text></g>)}
 <polyline points={x.map((v,i)=>`${px(v)},${py(y[i])}`).join(' ')} fill="none" stroke="#23676a" strokeWidth="2"/><text x={w/2} y={h-10} textAnchor="middle">{xLabel}</text><text x="12" y="15">{yLabel}</text><text x={l} y={h-b+22}>{xmin.toPrecision(3)}</text><text x={w-r} y={h-b+22} textAnchor="end">{xmax.toPrecision(3)}</text></svg>
}
export function Network({inputs,result}){
 const groups=[inputs,result?.physical_hidden||[null,null,null],result?.physical_output||[null,null]];
 const pts=groups.map((g,k)=>g.map((_,i)=>({x:100+k*260,y:88+i*65+(4-g.length)*32.5})));
 return <svg className="network" viewBox="0 0 740 360" role="img" aria-label="Four input signals, three hidden neurons and two output neurons">
 {[0,1].flatMap(k=>pts[k].flatMap((a,i)=>pts[k+1].map((b,j)=><line key={`${k}-${i}-${j}`} x1={a.x+28} y1={a.y} x2={b.x-28} y2={b.y} stroke={k===0?'#c8d8d2':'#b9ced1'} strokeWidth="1.4"/>)))}
 {['Optical inputs','Hidden layer','Output layer'].map((v,k)=><text className="group-label" key={v} x={100+k*260} y="28" textAnchor="middle">{v}</text>)}
 {groups.flatMap((g,k)=>g.map((v,i)=><g key={`${k}-${i}`}><circle cx={pts[k][i].x} cy={pts[k][i].y} r="28" fill={k===2?'#173b42':'#f9faf6'} stroke={k===0?'#bb7830':'#578483'} strokeWidth="1.5"/><text x={pts[k][i].x} y={pts[k][i].y+5} textAnchor="middle" fill={k===2?'white':'#24393b'}>{v===null?'—':fmt(v,3)}</text></g>))}
 <text x="370" y="343" textAnchor="middle" className="graph-note">Behavioural neuron model · fixed 4–3–2 architecture</text></svg>
}
