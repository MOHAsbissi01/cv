"""Serve ./site at http://localhost:8000/cv/ so the local base path matches GitHub Pages.

Run from the repo root:  python scripts/serve.py [port]
"""
import http.server, socketserver, sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
PREFIX = "/cv/"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(SITE), **k)

    def translate_path(self, path):
        if path == "/cv":
            path = PREFIX
        if not path.startswith(PREFIX):
            return str(SITE / "__not_found__")  # anything outside /cv/ is a 404, like production
        return super().translate_path("/" + path[len(PREFIX):])

    def send_error(self, code, message=None, explain=None):
        if code == 404 and (SITE / "404.html").exists():
            body = (SITE / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
        else:
            super().send_error(code, message, explain)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as srv:
        print(f"Serving {SITE} at http://localhost:{port}{PREFIX}")
        srv.serve_forever()
