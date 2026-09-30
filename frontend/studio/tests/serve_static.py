"""Serve a Pages-like repository subpath for frontend regression checks."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

dist = Path(__file__).resolve().parents[1] / "dist"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(dist), **kwargs)

    def do_GET(self):
        if not self.path.startswith("/Prabha/"):
            self.send_error(404)
            return
        self.path = self.path[len("/Prabha"):]
        super().do_GET()

    def log_message(self, *args):
        pass

ThreadingHTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
