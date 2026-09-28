"""PyInstaller entry point. Only JSON simulation operations are accepted."""
import json, sys
from prabha.product import dispatch
if __name__ == '__main__':
    try:
        text = sys.argv[1] if len(sys.argv) == 2 else sys.stdin.read(16001)
        if len(text.encode()) > 16000: raise ValueError('Desktop preview request limit: 16 KB')
        result = dispatch(json.loads(text))
    except (ValueError, TypeError) as exc:
        result = {'ok':False,'error':str(exc)}
    print(json.dumps(result, allow_nan=False))
