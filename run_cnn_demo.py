"""Launch the complete CNN demonstration without Node, PyTorch or a GPU."""
import os
for _name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[_name]='1'
from pathlib import Path
import argparse,json,sys,threading,webbrowser
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'core-py'))
from prabha.product import dispatch,VERSION


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'frontend/studio/public'),**kwargs)
    def do_GET(self):
        if urlsplit(self.path).path=='/api/health':return self.json_response({'ok':True,'version':VERSION,'engine':'native-python'})
        if urlsplit(self.path).path=='/':self.path='/cnn-demo.html'
        return super().do_GET()
    def json_response(self,data,status=200):
        encoded=json.dumps(data,allow_nan=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(encoded)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(encoded)
    def do_POST(self):
        if urlsplit(self.path).path!='/api/execute':return self.json_response({'ok':False,'error':'Unknown endpoint.'},404)
        origin=self.headers.get('Origin')
        if origin and urlsplit(origin).netloc!=self.headers.get('Host'):
            return self.json_response({'ok':False,'error':'Only same-origin demo requests are accepted.'},403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=1_000_000:raise ValueError('Request body must contain at most 1 MB of JSON.')
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict) or payload.get('action') not in {'cnn_info','cnn','cnn_validate','cnn_inspect'}:
                raise ValueError('This demo accepts only CNN workspace requests.')
            with self.server.compute_lock:result=dispatch(payload)
            self.json_response(result,200 if result['ok'] else 422)
        except (ValueError,UnicodeDecodeError) as error:self.json_response({'ok':False,'error':str(error)},400)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8765);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    check=dispatch({'action':'cnn_info'})
    if not check['ok']:raise SystemExit(check['error'])
    try:server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except OSError as error:raise SystemExit(f'Could not open port {args.port}. Close the previous demo or use --port 8766. {error}')
    server.compute_lock=threading.Lock()
    url=f'http://127.0.0.1:{server.server_address[1]}/'
    print('Prabha trained CNN demo: '+url,flush=True);print('Press Run live comparison. Close this terminal or press Ctrl+C to stop.',flush=True)
    if not args.no_browser:threading.Timer(.25,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
