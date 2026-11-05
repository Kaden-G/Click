#!/usr/bin/env python3
"""Serve Click locally and route its AI calls to your configured model.

    python3 serve.py            # http://127.0.0.1:8765
    python3 serve.py --port 9000 --open

Listens on 127.0.0.1 only. Your API key stays in this process; the page never
sees it. Prompts and answers are never logged.
"""
import argparse, json, pathlib, sys, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import llm

ROOT = pathlib.Path(__file__).parent
MAX_BODY = 1_000_000


class Handler(SimpleHTTPRequestHandler):
    cfg = None
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                      ".json": "application/json; charset=utf-8"}

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT / "dist"), **kw)

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            return self._json(200, {"ok": True, "provider": self.cfg["provider"], "model": self.cfg["model"]})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/llm":
            return self._json(404, {"error": "Not found"})
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BODY:
            return self._json(413, {"error": "Request too large", "code": "local_error"})
        try:
            prompt = json.loads(self.rfile.read(n))["prompt"]
            text = llm.complete(str(prompt), self.cfg)
            if not text.strip():
                return self._json(502, {"error": "Empty reply from model", "code": "local_error"})
            return self._json(200, {"text": text})
        except llm.LLMError as e:
            sys.stderr.write(f"[click] model error: {e}\n")
            return self._json(502, {"error": str(e), "code": "local_error"})
        except (ValueError, KeyError):
            return self._json(400, {"error": "Bad request", "code": "local_error"})

    def log_message(self, fmt, *args):
        if "/api/llm" not in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open Click in your browser")
    args = ap.parse_args()
    if not (ROOT / "dist/index.html").exists():
        sys.exit("dist/index.html is missing. Run: python3 build.py")
    try:
        Handler.cfg = llm.load_config()
        llm._key(Handler.cfg)
    except llm.LLMError as e:
        sys.exit(str(e))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Click running at {url}  (model: {Handler.cfg['model']} via {Handler.cfg['provider']})  Ctrl+C to stop")
    if args.open:
        webbrowser.open(url)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
