#!/usr/bin/env python3
"""
Simple mock HTTP server to simulate API endpoints used by the frontend during local development.
Serves:
  - GET /get_listing_by_geoid?geoid=...
  - GET /get_listings

Run: python3 mock_server.py
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

SAMPLE_LISTING = {
    'id': '11111111-1111-1111-1111-111111111111',
    'title': 'Phòng trọ thử nghiệm gần Cầu Giấy',
    'full_geo_id': '29CG.0AB01',
    'price_monthly_vnd': 3500000,
    'address_ward': 'Cầu Giấy',
    'address_street': 'Phạm Hùng',
}

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == '/get_listing_by_geoid':
            geoid = (qs.get('geoid') or [None])[0]
            if not geoid:
                self._send_json(400, {'error': 'missing geoid'})
                return
            norm = geoid.replace('.', '').upper()
            if norm in (SAMPLE_LISTING['full_geo_id'].replace('.', '').upper(), '29CGAB1'):
                self._send_json(200, SAMPLE_LISTING)
            else:
                self._send_json(404, {'error': 'not found'})
            return

        if path == '/get_listings':
            # Return array of listings
            self._send_json(200, [SAMPLE_LISTING])
            return

        if path == '/get_admin_listings':
            self._send_json(200, {'listings': [SAMPLE_LISTING]})
            return

        # Default
        self._send_json(404, {'error': 'unknown endpoint'})

    def log_message(self, format, *args):
        # Silence default logging to keep terminal clean
        return

if __name__ == '__main__':
    port = 5000
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f"Mock API server running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping mock server')
        server.server_close()
