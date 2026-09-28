"""HTTP transport for the shared Prabha operations."""
from pathlib import Path
import json, os, sys, asyncio
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'core-py'))
from prabha.product import dispatch, VERSION
app = FastAPI(title='Prabha simulation API', version=VERSION)
slots = asyncio.Semaphore(2)

@app.get('/api/health')
def health():
    return {'ok': True, 'version': VERSION, 'engine': 'native-python'}

async def perform(request, action=None):
    try:
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 1_000_000:
                raise ValueError('Request exceeds the 1 MB preview limit.')
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError('Request must be a JSON object.')
        if action: payload['action'] = action
    except (ValueError, UnicodeDecodeError) as exc:
        return JSONResponse({'ok': False, 'error': str(exc)}, status_code=400)
    async with slots:
        result = await asyncio.to_thread(dispatch, payload)
    return JSONResponse(result, status_code=200 if result['ok'] else 422)

@app.post('/api/execute')
async def execute(request: Request):
    return await perform(request)

@app.get('/api/blocks')
def blocks():
    return dispatch({'action': 'blocks'})['result']

@app.post('/api/run')
async def legacy_run(request: Request):
    response = await perform(request, 'graph')
    parsed = json.loads(response.body)
    if parsed['ok']: parsed = {'ok': True, **parsed['result']}
    return JSONResponse(parsed, status_code=response.status_code)

@app.get('/designer')
def designer():
    return FileResponse(ROOT / 'frontend/web/index.html')

dist = ROOT / 'frontend/studio/dist'
if dist.exists():
    app.mount('/', StaticFiles(directory=dist, html=True), name='studio')
else:
    @app.get('/')
    def build_required():
        return {'message': 'Build frontend/studio, or run its Vite dev server.', 'api': '/api/health'}

if __name__ == '__main__':
    uvicorn.run(app, host=os.environ.get('HOST', '127.0.0.1'), port=int(os.environ.get('PORT', 8000)))
