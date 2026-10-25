"""Launch the built Prabha Studio with the shared ANN/CNN Python API."""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_name, '1')
from pathlib import Path
import argparse
import socket
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--workspace', choices=['start', 'ann', 'cnn', 'neuron', 'components', 'evidence'], default='cnn')
    args = parser.parse_args()
    if not (ROOT / 'frontend/studio/dist/index.html').is_file():
        raise SystemExit('Studio has not been built. Run python scripts/build_web_assets.py, then npm run build --prefix frontend/studio.')
    import uvicorn
    from frontend.web.server import app
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        try:
            listener.bind(('127.0.0.1', args.port))
        except OSError as error:
            raise SystemExit(f'Could not open port {args.port}. Close the old Studio or use --port 8001. {error}') from error
        url = f'http://127.0.0.1:{listener.getsockname()[1]}/#{args.workspace}'
        print('Prabha Studio: ' + url, flush=True)
        print('ANN and CNN use the local Python engine. Press Ctrl+C to stop.', flush=True)
        if not args.no_browser:
            opener = threading.Timer(.8, lambda: webbrowser.open(url))
            opener.daemon = True
            opener.start()
        server = uvicorn.Server(uvicorn.Config(app, log_level='warning'))
        server.run(sockets=[listener])


if __name__ == '__main__':
    main()
