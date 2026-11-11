#!/usr/bin/env python3
"""
Backend Seguro para o Portfólio de Heloisa Cunha
------------------------------------------------
Recursos de Segurança Implementados:
1. Bloqueio estrito de arquivos sensíveis (.json, .py, .git, .env, .md) contra downloads não autorizados.
2. Endpoint GET /api/contact protegido por Token de Administrador (evita vazamento de dados de clientes/LGPD).
3. Rate Limiting por IP (proteção contra flooding e spam no formulário).
4. Sanitização e validação de tamanho de campos contra injeção e sobrecarga de memória.
5. Headers modernos de segurança HTTP (nosniff, SAMEORIGIN, XSS-Protection).
6. Zero dependências externas: utiliza exclusivamente a biblioteca padrão do Python 3.
"""

import http.server
import json
import os
import sys
import re
import html
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 14726
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(BASE_DIR, 'messages.json')

# Token de Administrador para leitura dos contatos (pode ser sobrescrito por variável de ambiente)
# Para ler os contatos no navegador: https://heloisa.neubas.com.br/api/contact?token=heloisa_admin_2026_sec
ADMIN_TOKEN = os.environ.get('PORTFOLIO_ADMIN_TOKEN', 'heloisa_admin_2026_sec')

# Extensões e arquivos protegidos que NUNCA devem ser baixados via HTTP direto
FORBIDDEN_EXTENSIONS = ('.json', '.py', '.git', '.env', '.md', '.sh', '.log', '.bak')
FORBIDDEN_FILES = ('server.py', 'messages.json', 'README.md', '.gitignore')

# Rate Limiting em memória: máximo 5 envios por IP a cada 10 minutos (600 segundos)
RATE_LIMIT_WINDOW = 600
RATE_LIMIT_MAX_SUBMISSIONS = 5
IP_SUBMISSIONS_LOG = {}

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

class SecurePortfolioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Log limpo no terminal com timestamp
        sys.stderr.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}\n")

    def send_security_headers(self):
        """Aplica cabeçalhos defensivos modernos de segurança HTTP"""
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')

    def send_json(self, status_code, data):
        response_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_security_headers()
        self.end_headers()

    def is_path_forbidden(self, path):
        """Verifica se a URL tenta acessar arquivos sensíveis ou ocultos"""
        clean_path = path.split('?')[0].lower()
        
        # Bloqueia pastas ocultas como .git
        if '/.' in clean_path or clean_path.startswith('.'):
            return True

        # Bloqueia arquivos proibidos por nome exato
        basename = os.path.basename(clean_path)
        if basename in FORBIDDEN_FILES:
            return True

        # Bloqueia arquivos proibidos por extensão
        if clean_path.endswith(FORBIDDEN_EXTENSIONS):
            return True

        return False

    def do_GET(self):
        parsed = urlparse(self.path)

        # 1. Bloqueio de arquivos sensíveis (messages.json, server.py, .git, etc.)
        if self.is_path_forbidden(self.path):
            self.send_response(403)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(b"403 Forbidden: Acesso restrito a este recurso.")
            return

        # 2. Endpoint de leitura dos contatos (/api/contact) protegido por autenticação
        if parsed.path == '/api/contact':
            auth_header = self.headers.get('Authorization', '')
            query_params = parse_qs(parsed.query)
            token_param = query_params.get('token', [''])[0]

            # Valida o token de administrador
            if not (auth_header == f"Bearer {ADMIN_TOKEN}" or token_param == ADMIN_TOKEN):
                self.send_json(401, {
                    'error': 'Não autorizado: token de administrador ausente ou inválido.',
                    'hint': 'Para acessar como administradora, use: /api/contact?token=SEU_TOKEN'
                })
                return

            messages = []
            if os.path.exists(MESSAGES_FILE):
                try:
                    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                except Exception:
                    messages = []

            self.send_json(200, {
                'status': 'ok',
                'count': len(messages),
                'messages': messages
            })
            return

        # Serve arquivos estáticos normalmente (HTML, CSS, Imagens, JS)
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/contact':
            client_ip = self.client_address[0]
            # Captura IP real caso esteja atrás do Nginx com X-Real-IP ou X-Forwarded-For
            if self.headers.get('X-Real-IP'):
                client_ip = self.headers.get('X-Real-IP')
            elif self.headers.get('X-Forwarded-For'):
                client_ip = self.headers.get('X-Forwarded-For').split(',')[0].strip()

            now = time.time()

            # 1. Rate Limiting por IP (Proteção contra Spam / DoS)
            history = IP_SUBMISSIONS_LOG.get(client_ip, [])
            recent_submissions = [t for t in history if now - t < RATE_LIMIT_WINDOW]
            IP_SUBMISSIONS_LOG[client_ip] = recent_submissions

            if len(recent_submissions) >= RATE_LIMIT_MAX_SUBMISSIONS:
                self.send_json(429, {
                    'error': 'Muitas mensagens enviadas em pouco tempo. Por favor, aguarde alguns minutos antes de tentar novamente.'
                })
                return

            try:
                content_length = int(self.headers.get('Content-Length', 0))
                # Limite estrito de 32 KB por mensagem
                if content_length <= 0 or content_length > 1024 * 32:
                    self.send_json(400, {'error': 'Corpo de requisição inválido ou excedeu o tamanho permitido.'})
                    return

                raw_body = self.rfile.read(content_length)
                data = json.loads(raw_body.decode('utf-8'))

                # 2. Honeypot check (se bot preencher campo armadilha invisível)
                if data.get('bot_trap') or data.get('website'):
                    # Retorna sucesso falso para enganar bots sem salvar nada
                    self.send_json(200, {'status': 'success', 'message': 'Mensagem recebida.'})
                    return

                # 3. Sanitização e Validação rigorosa dos campos
                name = str(data.get('name', '')).strip()
                email = str(data.get('email', '')).strip()
                subject = str(data.get('subject', 'Contato via Portfólio')).strip()
                message = str(data.get('message', '')).strip()
                lang = str(data.get('lang', 'pt')).strip()

                if not name or not email or not message:
                    self.send_json(400, {'error': 'Nome, e-mail e mensagem são campos obrigatórios.'})
                    return

                if len(name) < 2 or len(name) > 100:
                    self.send_json(400, {'error': 'O nome deve ter entre 2 e 100 caracteres.'})
                    return

                if len(email) > 120 or not EMAIL_REGEX.match(email):
                    self.send_json(400, {'error': 'Por favor, insira um endereço de e-mail válido.'})
                    return

                if len(subject) > 150:
                    subject = subject[:150]

                if len(message) < 5 or len(message) > 4000:
                    self.send_json(400, {'error': 'A mensagem deve ter entre 5 e 4000 caracteres.'})
                    return

                # Escape HTML defensivo contra injeção de scripts (XSS)
                safe_name = html.escape(name)
                safe_email = html.escape(email)
                safe_subject = html.escape(subject)
                safe_message = html.escape(message)

                new_entry = {
                    'id': int(datetime.utcnow().timestamp() * 1000),
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'date_human': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'name': safe_name,
                    'email': safe_email,
                    'subject': safe_subject,
                    'message': safe_message,
                    'lang': lang,
                    'client_ip': client_ip
                }

                # Atualiza registro de rate limit para o IP
                IP_SUBMISSIONS_LOG[client_ip].append(now)

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
                print(f"✨ NOVO CONTATO RECEBIDO (VALIDADO COM SUCESSO)")
                print(f"👤 De: {safe_name} <{safe_email}>")
                print(f"📌 Assunto: {safe_subject}")
                print(f"🌐 IP: {client_ip}")
                print(f"💬 Mensagem:\n{safe_message}")
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
    server = http.server.HTTPServer(('0.0.0.0', port), SecurePortfolioHandler)
    print(f"🛡️  Backend Seguro do Portfólio ativo em http://0.0.0.0:{port}")
    print(f"📁 Diretório raiz: {BASE_DIR}")
    print(f"🔒 Proteção ativa contra leitura de messages.json e arquivos sensíveis")
    print(f"🔑 Token admin configurado: {ADMIN_TOKEN}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
