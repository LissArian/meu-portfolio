#!/usr/bin/env python3
"""
Backend Server for Heloisa S. Cunha de Oliveira's Portfolio
-----------------------------------------------------------
Features:
- Static file server with optimized headers and correct MIME types.
- REST API endpoint:
    * POST /api/contact  -> Validates and saves lead messages to messages.json.
    * GET  /api/contact  -> Returns list of received contact inquiries.
- Zero external dependencies: uses Python 3 standard library.
"""

import http.server
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

PORT = 14726
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(BASE_DIR, 'messages.json')

class PortfolioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Custom clean logging
        sys.stderr.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}\n")

    def send_json(self, status_code, data):
        response_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/contact':
            if os.path.exists(MESSAGES_FILE):
                try:
                    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                except Exception:
                    messages = []
            else:
                messages = []
            self.send_json(200, {
                'status': 'ok',
                'count': len(messages),
                'messages': messages
            })
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/contact':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length <= 0 or content_length > 1024 * 64:  # max 64KB
                    self.send_json(400, {'error': 'Corpo de requisição inválido ou muito grande.'})
                    return

                raw_body = self.rfile.read(content_length)
                data = json.loads(raw_body.decode('utf-8'))

                name = str(data.get('name', '')).strip()
                email = str(data.get('email', '')).strip()
                subject = str(data.get('subject', 'Contato via Portfólio')).strip()
                message = str(data.get('message', '')).strip()
                lang = str(data.get('lang', 'pt')).strip()

                if not name or not email or not message:
                    self.send_json(400, {
                        'error': 'Campos obrigatórios ausentes: nome, e-mail e mensagem são necessários.'
                    })
                    return

                new_entry = {
                    'id': int(datetime.utcnow().timestamp() * 1000),
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'date_human': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'message': message,
                    'lang': lang,
                    'client_ip': self.client_address[0]
                }

                messages = []
                if os.path.exists(MESSAGES_FILE):
                    try:
                        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                    except Exception:
                        messages = []

                messages.append(new_entry)

                with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)

                print("\n" + "=" * 60)
                print(f"✨ NOVO CONTATO RECEBIDO NO PORTFÓLIO!")
                print(f"👤 De: {name} <{email}>")
                print(f"📌 Assunto: {subject}")
                print(f"💬 Mensagem:\n{message}")
                print("=" * 60 + "\n")

                msg_pt = "Mensagem recebida com sucesso! Em breve entrarei em contato."
                msg_en = "Message received successfully! I will get in touch shortly."

                self.send_json(200, {
                    'status': 'success',
                    'message': msg_en if lang == 'en' else msg_pt,
                    'id': new_entry['id']
                })
                return

            except json.JSONDecodeError:
                self.send_json(400, {'error': 'JSON inválido recebido.'})
                return
            except Exception as e:
                self.send_json(500, {'error': f'Erro interno do servidor: {str(e)}'})
                return

        self.send_json(404, {'error': 'Endpoint não encontrado.'})

if __name__ == '__main__':
    port = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    server = http.server.HTTPServer(('0.0.0.0', port), PortfolioHandler)
    print(f"🚀 Backend do Portfólio iniciado em http://localhost:{port}")
    print(f"📁 Diretório estático: {BASE_DIR}")
    print(f"📬 Endpoint de contato: POST http://localhost:{port}/api/contact")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
