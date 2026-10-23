import React, {useEffect, useRef, useState} from 'react';
import {saveText} from '../public/platform.js';

export default function CnnWorkspace({base, engine}) {
  const frame = useRef(null);
  const [height,setHeight] = useState(1700);
  useEffect(() => {
    const receive = async event => {
      if (event.source !== frame.current?.contentWindow || event.origin !== location.origin) return;
      const {id, payload, type} = event.data || {};
      if (type === 'prabha-cnn-height') {
        if (Number.isFinite(event.data.height)) setHeight(Math.max(900,Math.min(10000,event.data.height+20)));
        return;
      }
      if (!['prabha-cnn-request','prabha-cnn-save'].includes(type)) return;
      if (type === 'prabha-cnn-request' && !['cnn_info', 'cnn', 'cnn_validate', 'cnn_inspect'].includes(payload?.action)) return;
      try {
        let result;
        if (type === 'prabha-cnn-save') {
          const {name,text,mime} = event.data;
          if (!['prabha-cnn-settings.json','prabha-cnn-run.json','prabha-cnn-layer.json','prabha-cnn-results.csv'].includes(name) ||
              typeof text !== 'string' || text.length > 16000000) throw new Error('Invalid CNN export.');
          result = await saveText(name,text,mime==='text/csv'?'text/csv':'application/json');
        } else result = await (await engine).execute(payload);
        event.source.postMessage({type:'prabha-cnn-response', id, result}, event.origin);
      } catch (error) {
        event.source.postMessage({type:'prabha-cnn-response', id, error:error.message}, event.origin);
      }
    };
    window.addEventListener('message', receive);
    return () => window.removeEventListener('message', receive);
  }, [engine]);
  return <iframe ref={frame} src={base + 'cnn-demo.html?embedded=1'} title="Trained CNN comparison"
    style={{width:'100%',height:height+'px',border:0,borderRadius:'8px',background:'#f5f6f1'}}/>;
}
