#!/usr/bin/env python3
"""
StockRAG Live Server
Run: python server.py
Then open: http://localhost:8000/stockrag_dashboard.html
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

TD_KEY = 'e339963b13fa4dafb24a050bc3d817c3'
TD_BASE = 'https://api.twelvedata.com'

class Handler(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        # FIX 1: args[0] can be an HTTPStatus enum, not always a string.
        # Always convert to str before doing 'in' checks.
        msg = str(args[0]) if args else ''
        if '/td/' in msg:
            print(f'  📡 API: {msg}')
        elif '/favicon' in msg:
            pass  # silently ignore favicon noise
        elif '200' in msg or '304' in msg:
            pass  # suppress normal static-file hits to keep logs clean
        else:
            # show errors and anything unexpected
            print(f'  ℹ️  {msg}')

    def do_GET(self):
        # FIX 2: handle favicon.ico cleanly — return a 204 No Content
        # so the browser stops asking and the log stays clean.
        if self.path == '/favicon.ico':
            self.send_response(204)   # No Content
            self.end_headers()
            return

        # ── Proxy all /td/* requests to Twelve Data ──
        if self.path.startswith('/td/'):
            td_path = self.path[3:]          # strip /td  → keeps leading /
            url = TD_BASE + td_path
            sep = '&' if '?' in url else '?'
            url = url + sep + 'apikey=' + TD_KEY

            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'StockRAG/1.0'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
                print(f'  ✅ {td_path[:70]}')
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(
                    json.dumps({'code': 502, 'message': str(e)}).encode()
                )
                print(f'  ❌ {td_path[:70]} — {e}')
            return

        # ── Serve all other static files normally ──
        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()


if __name__ == '__main__':
    port = 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('localhost', port), Handler)
    print('=' * 55)
    print('  🚀  StockRAG Live Server')
    print('=' * 55)
    print(f'  📂  Serving:  {os.getcwd()}')
    print(f'  🌐  Open:     http://localhost:{port}/stockrag_dashboard.html')
    print(f'  📡  Proxy:    http://localhost:{port}/td/...')
    print(f'  🔑  API key:  {TD_KEY[:8]}...')
    print('=' * 55)
    print('  Press Ctrl+C to stop\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  🛑 Server stopped.')
